# test_simulation.py

import unittest
from unittest.mock import patch

from simulation.config import SimulationConfig
from simulation.exporters import (
    build_export_dataframes,
    build_runs_dataframe,
    dataframe_to_csv_bytes
)
from simulation.simulator import (
    Simulator,
    calculate_linear_trend,
    evaluate_run_acceptance
)


class PlantModelWithoutProcessing:
    """
    Modelo ficticio usado solo en pruebas.

    Reemplaza temporalmente PlantModel para evitar que triage,
    CRT o LCD retiren equipos del deposito durante la prueba.
    Asi se garantiza que el procesamiento sea igual a 0.
    """

    def __init__(self, *args, **kwargs):
        pass


class TestStorageCapacity(unittest.TestCase):
    """
    Pruebas automaticas de la capacidad fisica del deposito.
    """

    def test_full_storage_blocks_all_arrivals(self):

        config = SimulationConfig(
            days=1,
            inventory_capacity=300,
            initial_inventory=300,
            arrival_lambda=45,
            triage_servers=1,
            crt_servers=1,
            lcd_servers=1,
            workday_minutes=480,
            overtime_minutes=0
        )

        with patch(
            "simulation.simulator.PlantModel",
            PlantModelWithoutProcessing
        ), patch.object(
            Simulator,
            "_generate_arrivals",
            return_value=45
        ) as mock_arrivals:

            results = Simulator(config).run_single(seed=123)

        mock_arrivals.assert_called_once()

        self.assertEqual(
            results["FINAL_PHYSICAL_DEPOT_INVENTORY"],
            300
        )

        self.assertEqual(
            results["ADMITTED_EQUIPMENT"],
            0
        )

        self.assertEqual(
            results["BLOCKED_ARRIVALS"],
            45
        )

        self.assertEqual(
            results["TOTAL_ARRIVALS"],
            45
        )

        self.assertEqual(
            results["MAX_PHYSICAL_DEPOT_OCCUPANCY"],
            300
        )

        self.assertEqual(
            results["VIOLATION_COUNT"],
            0
        )

        self.assertTrue(
            results["CAPACITY_OK"]
        )

        self.assertFalse(
            results["IS_ACCEPTED"]
        )

    def test_capacity_is_respected_in_multiple_replications(self):

        config = SimulationConfig(
            days=30,
            runs=20,
            base_seed=1000,
            inventory_capacity=300,
            initial_inventory=100,
            arrival_lambda=45,
            triage_servers=1,
            crt_servers=2,
            lcd_servers=1,
            workday_minutes=480,
            overtime_minutes=120
        )

        with patch(
            "simulation.simulator.PlantModel",
            PlantModelWithoutProcessing
        ):
            experiment = Simulator(config).run_multiple()

        self.assertEqual(
            len(experiment["RUN_RESULTS"]),
            20
        )

        for result in experiment["RUN_RESULTS"]:

            with self.subTest(run_id=result["RUN_ID"]):

                self.assertLessEqual(
                    result["MAX_PHYSICAL_DEPOT_OCCUPANCY"],
                    config.inventory_capacity
                )

                self.assertEqual(
                    result["VIOLATION_COUNT"],
                    0
                )

                self.assertTrue(
                    result["CAPACITY_OK"]
                )

                self.assertEqual(
                    len(result["PHYSICAL_DEPOT_HISTORY"]),
                    config.days
                )


class TestMultipleRuns(unittest.TestCase):

    def test_seed_reproduces_single_run(self):

        config = SimulationConfig(
            days=10,
            inventory_capacity=300,
            initial_inventory=100,
            arrival_lambda=45,
            triage_servers=1,
            crt_servers=2,
            lcd_servers=1
        )

        simulator = Simulator(config)

        result_a = simulator.run_single(seed=12345)
        result_b = simulator.run_single(seed=12345)

        self.assertEqual(
            result_a,
            result_b
        )

    def test_run_multiple_uses_base_seed_for_every_run_and_does_not_concatenate_days(self):

        config = SimulationConfig(
            days=5,
            runs=3,
            base_seed=100,
            inventory_capacity=300,
            initial_inventory=100,
            arrival_lambda=45,
            triage_servers=1,
            crt_servers=2,
            lcd_servers=1
        )

        experiment = Simulator(config).run_multiple()

        self.assertEqual(
            [
                result["SEED"]
                for result in experiment["RUN_RESULTS"]
            ],
            [100, 100, 100]
        )

        reference = dict(
            experiment["RUN_RESULTS"][0]
        )
        reference.pop("RUN_ID")

        for result in experiment["RUN_RESULTS"][1:]:

            comparable = dict(result)
            comparable.pop("RUN_ID")

            self.assertEqual(
                comparable,
                reference
            )

        repeated_experiment = Simulator(config).run_multiple()

        self.assertEqual(
            repeated_experiment["RUN_RESULTS"],
            experiment["RUN_RESULTS"]
        )

        self.assertEqual(
            repeated_experiment["AGGREGATED_RESULTS"],
            experiment["AGGREGATED_RESULTS"]
        )

        self.assertEqual(
            len(experiment["AGGREGATED_RESULTS"]["DAYS"]),
            config.days
        )

        for result in experiment["RUN_RESULTS"]:

            self.assertEqual(
                len(result["DAYS"]),
                config.days
            )

            self.assertEqual(
                len(result["COST_HISTORY"]),
                config.days
            )

    def test_single_run_aggregate_matches_individual_result(self):

        config = SimulationConfig(
            days=7,
            runs=1,
            base_seed=50,
            inventory_capacity=300,
            initial_inventory=100,
            arrival_lambda=45,
            triage_servers=1,
            crt_servers=2,
            lcd_servers=1
        )

        experiment = Simulator(config).run_multiple()

        individual = experiment["RUN_RESULTS"][0]
        aggregated = experiment["AGGREGATED_RESULTS"]

        self.assertEqual(
            aggregated["METRICS"]["TOTAL_COST"]["MEAN"],
            individual["TOTAL_COST"]
        )

        self.assertEqual(
            aggregated["METRICS"]["FINAL_TOTAL_INVENTORY"]["MEAN"],
            individual["FINAL_TOTAL_INVENTORY"]
        )

        self.assertEqual(
            aggregated["PHYSICAL_DEPOT_HISTORY"],
            individual["PHYSICAL_DEPOT_HISTORY"]
        )

    def test_acceptance_summary_calculates_rate(self):

        config = SimulationConfig(
            minimum_acceptance_rate=0.95
        )

        summary = Simulator(config).acceptance_summary([
            {
                "IS_ACCEPTED": True,
                "REJECTION_REASONS": []
            },
            {
                "IS_ACCEPTED": False,
                "REJECTION_REASONS": [
                    "Dependencia excesiva de horas extra."
                ]
            },
        ])

        self.assertEqual(
            summary["RUNS_EXECUTED"],
            2
        )

        self.assertEqual(
            summary["ACCEPTED_RUNS"],
            1
        )

        self.assertEqual(
            summary["ACCEPTANCE_RATE"],
            50.0
        )

        self.assertFalse(
            summary["IS_SCENARIO_ACCEPTED"]
        )


class TestAcceptanceCriteria(unittest.TestCase):

    def test_rejection_reasons_are_registered(self):

        config = SimulationConfig(
            max_blocked_percentage=0.05,
            max_overtime_percentage=0.10
        )

        result = evaluate_run_acceptance(
            {
                "BLOCKED_PERCENTAGE": 6,
                "OVERTIME_PERCENTAGE": 11,
                "VIOLATION_COUNT": 1,
            },
            config
        )

        self.assertFalse(
            result["IS_ACCEPTED"]
        )

        self.assertEqual(
            len(result["REJECTION_REASONS"]),
            3
        )

    def test_inventory_growth_does_not_reject_run(self):

        config = SimulationConfig()

        result = evaluate_run_acceptance(
            {
                "BLOCKED_PERCENTAGE": 0,
                "OVERTIME_PERCENTAGE": 0,
                "VIOLATION_COUNT": 0,
            },
            config
        )

        self.assertTrue(
            result["IS_ACCEPTED"]
        )

        self.assertEqual(
            result["REJECTION_REASONS"],
            []
        )

    def test_excessive_blocking_rejects_run(self):

        config = SimulationConfig(
            max_blocked_percentage=0.05
        )

        result = evaluate_run_acceptance(
            {
                "BLOCKED_PERCENTAGE": 6,
                "OVERTIME_PERCENTAGE": 0,
                "VIOLATION_COUNT": 0,
            },
            config
        )

        self.assertFalse(
            result["IS_ACCEPTED"]
        )

        self.assertIn(
            "Porcentaje de ingresos bloqueados superior al permitido.",
            result["REJECTION_REASONS"]
        )

    def test_excessive_overtime_rejects_run(self):

        config = SimulationConfig(
            max_overtime_percentage=0.10
        )

        result = evaluate_run_acceptance(
            {
                "BLOCKED_PERCENTAGE": 0,
                "OVERTIME_PERCENTAGE": 11,
                "VIOLATION_COUNT": 0,
            },
            config
        )

        self.assertFalse(
            result["IS_ACCEPTED"]
        )

        self.assertIn(
            "Dependencia excesiva de horas extra.",
            result["REJECTION_REASONS"]
        )

    def test_violation_never_accepts_run(self):

        config = SimulationConfig()

        result = evaluate_run_acceptance(
            {
                "BLOCKED_PERCENTAGE": 0,
                "OVERTIME_PERCENTAGE": 0,
                "VIOLATION_COUNT": 1,
            },
            config
        )

        self.assertFalse(
            result["IS_ACCEPTED"]
        )

        self.assertIn(
            "Se detectaron violaciones de restricciones.",
            result["REJECTION_REASONS"]
        )


class TestVisualTrends(unittest.TestCase):

    def test_linear_trend_keeps_same_length_as_simulated_days(self):

        days = [1, 2, 3, 4]
        values = [10, 12, 14, 16]

        trend = calculate_linear_trend(
            days,
            values
        )

        self.assertEqual(
            len(trend["TREND_VALUES"]),
            len(days)
        )

        self.assertGreater(
            trend["SLOPE"],
            0
        )

    def test_aggregated_trends_are_based_on_daily_average_history(self):

        config = SimulationConfig(
            days=3
        )

        run_results = [
            {
                "CRT_PROCESSED": 0,
                "LCD_PROCESSED": 0,
                "IRRECOVERABLE_PROCESSED": 0,
                "TOTAL_PROCESSED": 0,
                "TOTAL_COST": 60,
                "CRT_LCD_PROCESSING_COST": 0,
                "BASE_SALARY_COST": 60,
                "OVERTIME_COST": 0,
                "FINAL_TOTAL_INVENTORY": 20,
                "FINAL_PHYSICAL_DEPOT_INVENTORY": 20,
                "AVERAGE_SYSTEM_INVENTORY": 20,
                "TOTAL_ARRIVALS": 0,
                "ADMITTED_EQUIPMENT": 0,
                "BLOCKED_ARRIVALS": 0,
                "BLOCKED_PERCENTAGE": 0,
                "MAX_PHYSICAL_DEPOT_OCCUPANCY": 30,
                "VIOLATION_COUNT": 0,
                "OVERTIME_DAYS_USED": 0,
                "OVERTIME_PERCENTAGE": 0,
                "DAYS": [1, 2, 3],
                "INVENTORY_HISTORY": [10, 20, 30],
                "PHYSICAL_DEPOT_HISTORY": [10, 20, 30],
                "ADMITTED_DAILY_HISTORY": [0, 0, 0],
                "BLOCKED_DAILY_HISTORY": [0, 0, 0],
                "CRT_HISTORY": [0, 0, 0],
                "LCD_HISTORY": [0, 0, 0],
                "IRRECOVERABLE_HISTORY": [0, 0, 0],
                "COST_HISTORY": [10, 20, 30],
                "PROCESSING_COST_HISTORY": [0, 0, 0],
                "BASE_LABOR_COST_HISTORY": [10, 20, 30],
                "LABOR_COST_HISTORY": [10, 20, 30],
                "OVERTIME_EXTRA_COST_HISTORY": [0, 0, 0],
                "DAILY_COST_HISTORY": [10, 10, 10],
                "DAILY_PROCESSING_COST_HISTORY": [0, 0, 0],
                "DAILY_BASE_LABOR_COST_HISTORY": [10, 10, 10],
                "DAILY_LABOR_COST_HISTORY": [10, 10, 10],
                "DAILY_OVERTIME_EXTRA_COST_HISTORY": [0, 0, 0],
            },
            {
                "CRT_PROCESSED": 0,
                "LCD_PROCESSED": 0,
                "IRRECOVERABLE_PROCESSED": 0,
                "TOTAL_PROCESSED": 0,
                "TOTAL_COST": 120,
                "CRT_LCD_PROCESSING_COST": 0,
                "BASE_SALARY_COST": 120,
                "OVERTIME_COST": 0,
                "FINAL_TOTAL_INVENTORY": 40,
                "FINAL_PHYSICAL_DEPOT_INVENTORY": 40,
                "AVERAGE_SYSTEM_INVENTORY": 40,
                "TOTAL_ARRIVALS": 0,
                "ADMITTED_EQUIPMENT": 0,
                "BLOCKED_ARRIVALS": 0,
                "BLOCKED_PERCENTAGE": 0,
                "MAX_PHYSICAL_DEPOT_OCCUPANCY": 60,
                "VIOLATION_COUNT": 0,
                "OVERTIME_DAYS_USED": 0,
                "OVERTIME_PERCENTAGE": 0,
                "DAYS": [1, 2, 3],
                "INVENTORY_HISTORY": [20, 40, 60],
                "PHYSICAL_DEPOT_HISTORY": [20, 40, 60],
                "ADMITTED_DAILY_HISTORY": [0, 0, 0],
                "BLOCKED_DAILY_HISTORY": [0, 0, 0],
                "CRT_HISTORY": [0, 0, 0],
                "LCD_HISTORY": [0, 0, 0],
                "IRRECOVERABLE_HISTORY": [0, 0, 0],
                "COST_HISTORY": [20, 40, 60],
                "PROCESSING_COST_HISTORY": [0, 0, 0],
                "BASE_LABOR_COST_HISTORY": [20, 40, 60],
                "LABOR_COST_HISTORY": [20, 40, 60],
                "OVERTIME_EXTRA_COST_HISTORY": [0, 0, 0],
                "DAILY_COST_HISTORY": [20, 20, 20],
                "DAILY_PROCESSING_COST_HISTORY": [0, 0, 0],
                "DAILY_BASE_LABOR_COST_HISTORY": [20, 20, 20],
                "DAILY_LABOR_COST_HISTORY": [20, 20, 20],
                "DAILY_OVERTIME_EXTRA_COST_HISTORY": [0, 0, 0],
            },
        ]

        aggregated = Simulator(config).aggregate_results(
            run_results
        )

        self.assertEqual(
            aggregated["PHYSICAL_DEPOT_AVERAGE_HISTORY"],
            [15.0, 30.0, 45.0]
        )

        self.assertEqual(
            aggregated["PHYSICAL_DEPOT_TREND_HISTORY"],
            [15.0, 30.0, 45.0]
        )

        self.assertEqual(
            len(aggregated["COST_TREND_HISTORY"]),
            len(aggregated["DAYS"])
        )


class TestCsvExporters(unittest.TestCase):

    def test_single_run_csv_has_one_row(self):

        config = SimulationConfig(
            days=3,
            runs=1,
            base_seed=10
        )

        experiment = Simulator(config).run_multiple()
        dataframes = build_export_dataframes(
            experiment
        )

        self.assertEqual(
            len(dataframes["runs"]),
            1
        )

        self.assertEqual(
            dataframes["runs"].iloc[0]["SCENARIO_ID"],
            experiment["SCENARIO_ID"]
        )

    def test_ten_run_csv_has_ten_rows_and_repeated_base_seed(self):

        config = SimulationConfig(
            days=2,
            runs=10,
            base_seed=1
        )

        experiment = Simulator(config).run_multiple()
        dataframes = build_export_dataframes(
            experiment
        )

        seeds = dataframes["runs"]["SEED"].tolist()

        self.assertEqual(
            len(dataframes["runs"]),
            10
        )

        self.assertEqual(
            seeds,
            [1] * 10
        )

        metric_columns = [
            "TOTAL_COST",
            "BLOCKED_PERCENTAGE_PCT",
            "OVERTIME_PERCENTAGE_PCT",
            "FINAL_TOTAL_INVENTORY",
        ]

        for column in metric_columns:

            self.assertEqual(
                dataframes["runs"][column].nunique(),
                1
            )

    def test_exported_parameters_match_executed_config_snapshot(self):

        config = SimulationConfig(
            days=4,
            runs=2,
            base_seed=55,
            inventory_capacity=250,
            max_blocked_percentage=0.07,
            max_overtime_percentage=0.12,
            minimum_acceptance_rate=0.90
        )

        experiment = Simulator(config).run_multiple()
        runs_df = build_export_dataframes(
            experiment
        )["runs"]

        row = runs_df.iloc[0]

        self.assertEqual(
            row["PARAM_DAYS"],
            4
        )

        self.assertEqual(
            row["PARAM_RUNS"],
            2
        )

        self.assertEqual(
            row["PARAM_BASE_SEED"],
            55
        )

        self.assertEqual(
            row["PARAM_INVENTORY_CAPACITY"],
            250
        )

        self.assertAlmostEqual(
            row["PARAM_MAX_BLOCKED_PERCENTAGE_PCT"],
            7.0
        )

        self.assertEqual(
            row["PARAM_MAX_OVERTIME_PERCENTAGE_PCT"],
            12.0
        )

        self.assertEqual(
            row["PARAM_MINIMUM_ACCEPTANCE_RATE_PCT"],
            90.0
        )

    def test_run_metrics_export_match_results(self):

        config = SimulationConfig(
            days=3,
            runs=1,
            base_seed=99
        )

        experiment = Simulator(config).run_multiple()
        run_result = experiment["RUN_RESULTS"][0]
        runs_df = build_export_dataframes(
            experiment
        )["runs"]
        row = runs_df.iloc[0]

        self.assertEqual(
            row["TOTAL_COST"],
            run_result["TOTAL_COST"]
        )

        self.assertEqual(
            row["BLOCKED_PERCENTAGE_PCT"],
            run_result["BLOCKED_PERCENTAGE"]
        )

        self.assertEqual(
            row["OVERTIME_PERCENTAGE_PCT"],
            run_result["OVERTIME_PERCENTAGE"]
        )

        self.assertEqual(
            row["IS_ACCEPTED"],
            run_result["IS_ACCEPTED"]
        )

    def test_daily_history_has_one_row_per_run_and_day(self):

        config = SimulationConfig(
            days=5,
            runs=3,
            base_seed=20
        )

        experiment = Simulator(config).run_multiple()
        daily_df = build_export_dataframes(
            experiment
        )["daily_history"]

        self.assertEqual(
            len(daily_df),
            15
        )

        for run_id in [1, 2, 3]:
            run_days = daily_df[
                daily_df["RUN_ID"] == run_id
            ]["DAY"].tolist()

            self.assertEqual(
                run_days,
                [1, 2, 3, 4, 5]
            )

    def test_rejection_reasons_and_violations_are_joined_as_text(self):

        config = SimulationConfig(
            days=1,
            runs=1
        )

        run_results = [{
            "RUN_ID": 1,
            "SEED": 123,
            "IS_ACCEPTED": False,
            "REJECTION_REASONS": [
                "Motivo A",
                "Motivo B"
            ],
            "VIOLATIONS": [
                "Violacion A",
                "Violacion B"
            ],
            "CRT_PROCESSED": 0,
            "LCD_PROCESSED": 0,
            "IRRECOVERABLE_PROCESSED": 0,
            "TOTAL_PROCESSED": 0,
            "TOTAL_COST": 0,
            "CRT_LCD_PROCESSING_COST": 0,
            "BASE_SALARY_COST": 0,
            "OVERTIME_COST": 0,
            "FINAL_TOTAL_INVENTORY": 0,
            "FINAL_PHYSICAL_DEPOT_INVENTORY": 0,
            "AVERAGE_SYSTEM_INVENTORY": 0,
            "TOTAL_ARRIVALS": 0,
            "ADMITTED_EQUIPMENT": 0,
            "BLOCKED_ARRIVALS": 0,
            "BLOCKED_PERCENTAGE": 0,
            "MAX_PHYSICAL_DEPOT_OCCUPANCY": 0,
            "OVERTIME_DAYS_USED": 0,
            "OVERTIME_PERCENTAGE": 0,
            "VIOLATION_COUNT": 2,
        }]

        runs_df = build_runs_dataframe(
            run_results,
            config,
            "ESC_TEST",
            "2026-06-27T15:30:00"
        )

        self.assertEqual(
            runs_df.iloc[0]["REJECTION_REASONS"],
            "Motivo A | Motivo B"
        )

        self.assertEqual(
            runs_df.iloc[0]["VIOLATIONS"],
            "Violacion A | Violacion B"
        )

    def test_summary_csv_contains_acceptance_block(self):

        config = SimulationConfig(
            days=2,
            runs=2,
            base_seed=5
        )

        experiment = Simulator(config).run_multiple()
        summary_df = build_export_dataframes(
            experiment
        )["summary"]

        metrics = summary_df["METRIC"].tolist()

        self.assertIn(
            "RUNS_EXECUTED",
            metrics
        )

        self.assertIn(
            "ACCEPTANCE_RATE_PCT",
            metrics
        )

        self.assertIn(
            "SCENARIO_IS_ACCEPTED",
            metrics
        )

    def test_csv_bytes_use_excel_friendly_format(self):

        config = SimulationConfig(
            days=1,
            runs=1,
            base_seed=1
        )

        experiment = Simulator(config).run_multiple()
        runs_df = build_export_dataframes(
            experiment
        )["runs"]

        csv_bytes = dataframe_to_csv_bytes(
            runs_df
        )

        self.assertTrue(
            csv_bytes.startswith(
                b"\xef\xbb\xbf"
            )
        )

        self.assertIn(
            b";",
            csv_bytes
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
