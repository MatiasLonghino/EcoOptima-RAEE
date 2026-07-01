from collections import Counter
from dataclasses import asdict
from datetime import datetime

import simpy
import numpy as np

from simulation.entities import Monitor
from simulation.stores import PlantStores
from simulation.statistics import Statistics
from simulation.model import PlantModel


MODEL_VERSION = "1.0"


def evaluate_run_acceptance(result, config):

    reasons = []

    if (
        result["BLOCKED_PERCENTAGE"]
        > config.max_blocked_percentage * 100
    ):
        reasons.append(
            "Porcentaje de ingresos bloqueados superior al permitido."
        )

    if (
        result["OVERTIME_PERCENTAGE"]
        > config.max_overtime_percentage * 100
    ):
        reasons.append(
            "Dependencia excesiva de horas extra."
        )

    if result["VIOLATION_COUNT"] > 0:
        reasons.append(
            "Se detectaron violaciones de restricciones."
        )

    result["REJECTION_REASONS"] = reasons
    result["IS_ACCEPTED"] = len(reasons) == 0

    return result


def calculate_linear_trend(days, values):

    if len(days) < 2 or len(values) < 2:
        return {
            "TREND_VALUES": list(values),
            "SLOPE": 0.0,
        }

    x = np.asarray(
        days,
        dtype=float
    )
    y = np.asarray(
        values,
        dtype=float
    )

    slope, intercept = np.polyfit(
        x,
        y,
        1
    )

    trend_values = (
        slope
        * x
        + intercept
    )

    return {
        "TREND_VALUES": [
            round(float(value), 2)
            for value in trend_values
        ],
        "SLOPE": round(
            float(slope),
            4
        ),
    }


class Simulator:

    AGGREGATED_METRICS = (
        "CRT_PROCESSED",
        "LCD_PROCESSED",
        "IRRECOVERABLE_PROCESSED",
        "TOTAL_PROCESSED",
        "TOTAL_COST",
        "CRT_LCD_PROCESSING_COST",
        "BASE_SALARY_COST",
        "OVERTIME_COST",
        "FINAL_TOTAL_INVENTORY",
        "FINAL_PHYSICAL_DEPOT_INVENTORY",
        "AVERAGE_SYSTEM_INVENTORY",
        "TOTAL_ARRIVALS",
        "ADMITTED_EQUIPMENT",
        "BLOCKED_ARRIVALS",
        "BLOCKED_PERCENTAGE",
        "MAX_PHYSICAL_DEPOT_OCCUPANCY",
        "VIOLATION_COUNT",
        "OVERTIME_DAYS_USED",
        "OVERTIME_PERCENTAGE",
    )

    HISTORY_KEYS = (
        "INVENTORY_HISTORY",
        "PHYSICAL_DEPOT_HISTORY",
        "ADMITTED_DAILY_HISTORY",
        "BLOCKED_DAILY_HISTORY",
        "CRT_HISTORY",
        "LCD_HISTORY",
        "IRRECOVERABLE_HISTORY",
        "COST_HISTORY",
        "PROCESSING_COST_HISTORY",
        "BASE_LABOR_COST_HISTORY",
        "LABOR_COST_HISTORY",
        "OVERTIME_EXTRA_COST_HISTORY",
        "DAILY_COST_HISTORY",
        "DAILY_PROCESSING_COST_HISTORY",
        "DAILY_BASE_LABOR_COST_HISTORY",
        "DAILY_LABOR_COST_HISTORY",
        "DAILY_OVERTIME_EXTRA_COST_HISTORY",
    )

    HISTORY_ALIASES = {
        "STORAGE_INVENTORY_HISTORY": "PHYSICAL_DEPOT_HISTORY",
        "ADMITTED_HISTORY": "ADMITTED_DAILY_HISTORY",
        "REJECTED_HISTORY": "BLOCKED_DAILY_HISTORY",
    }

    def __init__(self, config):

        self.config = config

    def run(self, seed=None):

        return self.run_single(seed=seed)

    def run_single(self, seed=None, run_id=1):

        seed = self._resolve_seed(seed, run_id)
        rng = np.random.default_rng(seed)

        stats = Statistics()
        env = simpy.Environment()

        stores = PlantStores(
            env,
            self.config.inventory_capacity
        )

        PlantModel(
            env,
            stores,
            self.config,
            stats,
            rng
        )

        monitor_id = 0
        overtime_next_day = False
        violations = []

        for _ in range(self.config.initial_inventory):

            monitor_id += 1

            stores.inventory.put(
                Monitor(monitor_id)
            )

        initial_storage_inventory = len(
            stores.inventory.items
        )

        stats.max_storage_inventory = (
            initial_storage_inventory
        )

        for day in range(1, self.config.days + 1):

            arrivals = self._generate_arrivals(rng)

            current_storage_inventory = len(
                stores.inventory.items
            )

            available_space = (
                self.config.inventory_capacity
                - current_storage_inventory
            )

            available_space = max(
                0,
                available_space
            )

            admitted = min(
                arrivals,
                available_space
            )

            rejected = arrivals - admitted

            for _ in range(admitted):

                monitor_id += 1

                stores.inventory.put(
                    Monitor(
                        monitor_id,
                        arrival_day=day
                    )
                )

            storage_inventory_after_arrivals = len(
                stores.inventory.items
            )

            stats.total_admitted += admitted
            stats.total_rejected += rejected

            stats.admitted_history.append(
                admitted
            )

            stats.rejected_history.append(
                rejected
            )

            stats.max_storage_inventory = max(
                stats.max_storage_inventory,
                storage_inventory_after_arrivals
            )

            if (
                storage_inventory_after_arrivals
                > self.config.inventory_capacity
            ):
                stats.capacity_violations += 1
                violations.append(
                    (
                        "Dia "
                        f"{day}: inventario fisico superior a la capacidad."
                    )
                )

            daily_minutes = self.config.workday_minutes

            employees = (
                self.config.triage_servers
                + self.config.crt_servers
                + self.config.lcd_servers
            )

            base_labor_cost = (
                employees
                * self.config.employee_daily_cost
            )

            overtime_extra_cost = 0

            if overtime_next_day:

                daily_minutes += self.config.overtime_minutes

                overtime_extra_cost = (
                    base_labor_cost
                    * 0.5
                )

                stats.overtime_days += 1

            daily_labor_cost = (
                base_labor_cost
                + overtime_extra_cost
            )

            stats.total_base_labor_cost += base_labor_cost
            stats.total_labor_cost += daily_labor_cost
            stats.total_overtime_extra_cost += overtime_extra_cost
            stats.total_cost += daily_labor_cost

            processing_cost_before_day = (
                stats.total_processing_cost
            )
            total_cost_before_day = (
                stats.total_cost
                - daily_labor_cost
            )

            env.run(
                until=env.now + daily_minutes
            )

            daily_processing_cost = (
                stats.total_processing_cost
                - processing_cost_before_day
            )

            daily_total_cost = (
                stats.total_cost
                - total_cost_before_day
            )

            inventory_level = self._system_inventory(
                stores,
                stats
            )

            storage_inventory = len(
                stores.inventory.items
            )

            stats.inventory_history.append(
                inventory_level
            )

            stats.storage_inventory_history.append(
                storage_inventory
            )

            stats.max_storage_inventory = max(
                stats.max_storage_inventory,
                storage_inventory
            )

            if (
                storage_inventory
                > self.config.inventory_capacity
            ):
                stats.capacity_violations += 1
                violations.append(
                    (
                        "Dia "
                        f"{day}: deposito fisico superior a la capacidad."
                    )
                )

            if inventory_level < 0 or storage_inventory < 0:
                violations.append(
                    f"Dia {day}: inventario negativo detectado."
                )

            stats.crt_history.append(
                stats.processed_crt
            )

            stats.lcd_history.append(
                stats.processed_lcd
            )

            stats.irrecoverable_history.append(
                stats.processed_irrecoverable
            )

            stats.cost_history.append(
                stats.total_cost
            )

            stats.processing_cost_history.append(
                stats.total_processing_cost
            )

            stats.base_labor_cost_history.append(
                stats.total_base_labor_cost
            )

            stats.labor_cost_history.append(
                stats.total_labor_cost
            )

            stats.overtime_extra_cost_history.append(
                stats.total_overtime_extra_cost
            )

            stats.daily_cost_history.append(
                daily_total_cost
            )

            stats.daily_processing_cost_history.append(
                daily_processing_cost
            )

            stats.daily_base_labor_cost_history.append(
                base_labor_cost
            )

            stats.daily_labor_cost_history.append(
                daily_labor_cost
            )

            stats.daily_overtime_extra_cost_history.append(
                overtime_extra_cost
            )

            threshold = (
                self.config.inventory_capacity
                * self.config.threshold_percentage
            )

            overtime_next_day = (
                inventory_level >= threshold
            )

        final_inventory = self._system_inventory(
            stores,
            stats
        )

        final_storage_inventory = len(
            stores.inventory.items
        )

        total_arrivals = (
            stats.total_admitted
            + stats.total_rejected
        )

        total_processed = (
            stats.processed_crt
            + stats.processed_lcd
            + stats.processed_irrecoverable
        )

        expected_equipment = (
            self.config.initial_inventory
            + stats.total_admitted
        )

        accounted_equipment = (
            total_processed
            + final_inventory
        )

        if expected_equipment != accounted_equipment:
            violations.append(
                (
                    "Inconsistencia contable entre equipos admitidos, "
                    "procesados e inventario final."
                )
            )

        blocked_percentage = 0.0
        if total_arrivals > 0:
            blocked_percentage = (
                stats.total_rejected
                / total_arrivals
            ) * 100

        overtime_percentage = (
            stats.overtime_days
            / self.config.days
        ) * 100

        result = {
            "RUN_ID": run_id,
            "SEED": seed,

            "CRT_PROCESSED": stats.processed_crt,
            "LCD_PROCESSED": stats.processed_lcd,
            "IRRECOVERABLE_PROCESSED": stats.processed_irrecoverable,
            "TOTAL_PROCESSED": total_processed,

            "TOTAL_COST": round(stats.total_cost, 2),
            "CRT_LCD_PROCESSING_COST": round(
                stats.total_processing_cost,
                2
            ),
            "BASE_SALARY_COST": round(
                stats.total_base_labor_cost,
                2
            ),
            "OVERTIME_COST": round(
                stats.total_overtime_extra_cost,
                2
            ),

            "FINAL_TOTAL_INVENTORY": final_inventory,
            "FINAL_PHYSICAL_DEPOT_INVENTORY":
                final_storage_inventory,
            "AVERAGE_SYSTEM_INVENTORY": round(
                stats.average_inventory(),
                2
            ),

            "TOTAL_ARRIVALS": total_arrivals,
            "ADMITTED_EQUIPMENT": stats.total_admitted,
            "BLOCKED_ARRIVALS": stats.total_rejected,
            "BLOCKED_PERCENTAGE": round(
                blocked_percentage,
                2
            ),

            "MAX_PHYSICAL_DEPOT_OCCUPANCY":
                stats.max_storage_inventory,
            "VIOLATION_COUNT": len(violations),
            "VIOLATIONS": violations,

            "OVERTIME_DAYS_USED": stats.overtime_days,
            "OVERTIME_PERCENTAGE": round(
                overtime_percentage,
                2
            ),

            "IS_ACCEPTED": False,
            "REJECTION_REASONS": [],

            "DAYS": list(
                range(
                    1,
                    self.config.days + 1
                )
            ),

            "INVENTORY_HISTORY": stats.inventory_history,
            "PHYSICAL_DEPOT_HISTORY":
                stats.storage_inventory_history,
            "ADMITTED_DAILY_HISTORY": stats.admitted_history,
            "BLOCKED_DAILY_HISTORY": stats.rejected_history,
            "CRT_HISTORY": stats.crt_history,
            "LCD_HISTORY": stats.lcd_history,
            "IRRECOVERABLE_HISTORY":
                stats.irrecoverable_history,
            "COST_HISTORY": stats.cost_history,
            "PROCESSING_COST_HISTORY":
                stats.processing_cost_history,
            "BASE_LABOR_COST_HISTORY":
                stats.base_labor_cost_history,
            "LABOR_COST_HISTORY":
                stats.labor_cost_history,
            "OVERTIME_EXTRA_COST_HISTORY":
                stats.overtime_extra_cost_history,
            "DAILY_COST_HISTORY": stats.daily_cost_history,
            "DAILY_PROCESSING_COST_HISTORY":
                stats.daily_processing_cost_history,
            "DAILY_BASE_LABOR_COST_HISTORY":
                stats.daily_base_labor_cost_history,
            "DAILY_LABOR_COST_HISTORY":
                stats.daily_labor_cost_history,
            "DAILY_OVERTIME_EXTRA_COST_HISTORY":
                stats.daily_overtime_extra_cost_history,
        }

        self._add_legacy_result_keys(
            result,
            stats
        )

        return evaluate_run_acceptance(
            result,
            self.config
        )

    def run_multiple(self, runs=None, base_seed=None):

        runs = self.config.runs if runs is None else int(runs)
        base_seed = (
            self.config.base_seed
            if base_seed is None
            else base_seed
        )

        if runs <= 0:
            raise ValueError(
                "La cantidad de corridas debe ser mayor que cero."
            )

        if base_seed is not None and base_seed < 0:
            raise ValueError(
                "La semilla base no puede ser negativa."
            )

        executed_at_dt = datetime.now()

        executed_at = executed_at_dt.replace(
            microsecond=0
        ).isoformat()

        scenario_id = self._build_scenario_id(
            executed_at_dt
        )

        config_snapshot = asdict(
            self.config
        )

        config_snapshot["runs"] = runs
        config_snapshot["base_seed"] = base_seed

        seeds = self._seeds_for_runs(
            runs,
            base_seed
        )

        run_results = []

        for run_id, seed in enumerate(seeds, start=1):

            run_results.append(
                self.run_single(
                    seed=seed,
                    run_id=run_id
                )
            )

        aggregated_results = self.aggregate_results(
            run_results
        )

        acceptance_summary = self.acceptance_summary(
            run_results
        )

        return {
            "SCENARIO_ID": scenario_id,
            "EXECUTED_AT": executed_at,
            "MODEL_VERSION": MODEL_VERSION,
            "CONFIG": config_snapshot,
            "RUN_RESULTS": run_results,
            "AGGREGATED_RESULTS": aggregated_results,
            "ACCEPTANCE_SUMMARY": acceptance_summary,
        }

    def aggregate_results(self, run_results):

        metrics = {}

        for metric in self.AGGREGATED_METRICS:

            values = [
                result[metric]
                for result in run_results
            ]

            metrics[metric] = self._summarize_values(
                values
            )

        daily_history_stats = {}

        for history_key in self.HISTORY_KEYS:

            history_stats = self._summarize_history(
                run_results,
                history_key
            )

            daily_history_stats[history_key] = history_stats

        days_length = min(
            (
                len(result["DAYS"])
                for result in run_results
            ),
            default=0
        )

        aggregated = {
            "METRICS": metrics,
            "DAILY_HISTORY_STATS": daily_history_stats,
            "DAYS": list(
                range(
                    1,
                    days_length + 1
                )
            ),
        }

        for history_key, history_stats in daily_history_stats.items():

            aggregated[history_key] = history_stats["MEAN"]

        for alias, source in self.HISTORY_ALIASES.items():

            aggregated[alias] = aggregated[source]

        physical_depot_trend = calculate_linear_trend(
            aggregated["DAYS"],
            aggregated["PHYSICAL_DEPOT_HISTORY"]
        )

        cost_trend = calculate_linear_trend(
            aggregated["DAYS"],
            aggregated["COST_HISTORY"]
        )

        aggregated.update({
            "PHYSICAL_DEPOT_AVERAGE_HISTORY":
                aggregated["PHYSICAL_DEPOT_HISTORY"],
            "PHYSICAL_DEPOT_TREND_HISTORY":
                physical_depot_trend["TREND_VALUES"],
            "PHYSICAL_DEPOT_TREND_SLOPE":
                physical_depot_trend["SLOPE"],
            "COST_AVERAGE_HISTORY":
                aggregated["COST_HISTORY"],
            "COST_TREND_HISTORY":
                cost_trend["TREND_VALUES"],
            "COST_TREND_SLOPE":
                cost_trend["SLOPE"],
        })

        return aggregated

    def acceptance_summary(self, run_results):

        runs_executed = len(run_results)

        accepted_runs = sum(
            1
            for result in run_results
            if result["IS_ACCEPTED"]
        )

        rejected_runs = (
            runs_executed
            - accepted_runs
        )

        acceptance_rate = 0.0

        if runs_executed > 0:
            acceptance_rate = (
                accepted_runs
                / runs_executed
            )

        reason_counter = Counter()

        for result in run_results:

            reason_counter.update(
                result["REJECTION_REASONS"]
            )

        reason_summary = []

        for reason, count in reason_counter.items():

            percentage = 0.0

            if runs_executed > 0:
                percentage = (
                    count
                    / runs_executed
                ) * 100

            reason_summary.append({
                "REASON": reason,
                "RUNS_AFFECTED": count,
                "PERCENTAGE": round(
                    percentage,
                    2
                ),
            })

        reason_summary.sort(
            key=lambda row: row["RUNS_AFFECTED"],
            reverse=True
        )

        return {
            "RUNS_EXECUTED": runs_executed,
            "ACCEPTED_RUNS": accepted_runs,
            "REJECTED_RUNS": rejected_runs,
            "ACCEPTANCE_RATE": round(
                acceptance_rate * 100,
                2
            ),
            "MINIMUM_ACCEPTANCE_RATE": round(
                self.config.minimum_acceptance_rate * 100,
                2
            ),
            "IS_SCENARIO_ACCEPTED": (
                acceptance_rate
                >= self.config.minimum_acceptance_rate
            ),
            "REJECTION_REASON_SUMMARY": reason_summary,
            "REJECTION_REASON_COUNTS": dict(
                reason_counter
            ),
        }

    def _resolve_seed(self, seed, run_id):

        if seed is not None:
            return int(seed)

        if self.config.base_seed is not None:
            return int(self.config.base_seed)

        return self._random_seeds(1)[0]

    def _seeds_for_runs(self, runs, base_seed):

        if base_seed is not None:
            return [
                int(base_seed)
                for _ in range(runs)
            ]

        return self._random_seeds(runs)

    def _random_seeds(self, count):

        seed_sequence = np.random.SeedSequence()

        return [
            int(
                child.generate_state(
                    1,
                    dtype=np.uint32
                )[0]
            )
            for child in seed_sequence.spawn(count)
        ]

    def _build_scenario_id(self, executed_at_dt):

        return (
            "ESC_"
            + executed_at_dt.strftime(
                "%Y%m%d_%H%M%S_%f"
            )
        )

    def _generate_arrivals(self, rng):

        return int(
            rng.poisson(
                self.config.arrival_lambda
            )
        )

    def _system_inventory(self, stores, stats):

        return (
            len(stores.inventory.items)
            + len(stores.crt_queue.items)
            + len(stores.lcd_queue.items)
            + stats.in_triage
            + stats.in_crt_processing
            + stats.in_lcd_processing
        )

    def _summarize_values(self, values):

        if not values:
            return {
                "MEAN": 0.0,
                "MIN": 0.0,
                "MAX": 0.0,
                "STD": 0.0,
            }

        data = np.array(
            values,
            dtype=float
        )

        return {
            "MEAN": round(
                float(np.mean(data)),
                2
            ),
            "MIN": round(
                float(np.min(data)),
                2
            ),
            "MAX": round(
                float(np.max(data)),
                2
            ),
            "STD": round(
                float(np.std(data)),
                2
            ),
        }

    def _summarize_history(self, run_results, history_key):

        if not run_results:
            return {
                "MEAN": [],
                "MIN": [],
                "MAX": [],
                "STD": [],
            }

        history_length = min(
            len(result.get(history_key, []))
            for result in run_results
        )

        if history_length == 0:
            return {
                "MEAN": [],
                "MIN": [],
                "MAX": [],
                "STD": [],
            }

        data = np.array(
            [
                result[history_key][:history_length]
                for result in run_results
            ],
            dtype=float
        )

        return {
            "MEAN": [
                round(float(value), 2)
                for value in np.mean(data, axis=0)
            ],
            "MIN": [
                round(float(value), 2)
                for value in np.min(data, axis=0)
            ],
            "MAX": [
                round(float(value), 2)
                for value in np.max(data, axis=0)
            ],
            "STD": [
                round(float(value), 2)
                for value in np.std(data, axis=0)
            ],
        }

    def _add_legacy_result_keys(self, result, stats):

        result.update({
            "CRT": result["CRT_PROCESSED"],
            "LCD": result["LCD_PROCESSED"],
            "IRRECOVERABLE": result["IRRECOVERABLE_PROCESSED"],
            "FINAL_INVENTORY": result["FINAL_TOTAL_INVENTORY"],
            "FINAL_STORAGE_INVENTORY":
                result["FINAL_PHYSICAL_DEPOT_INVENTORY"],
            "AVG_INVENTORY": result["AVERAGE_SYSTEM_INVENTORY"],
            "TOTAL_PROCESSING_COST":
                result["CRT_LCD_PROCESSING_COST"],
            "TOTAL_BASE_LABOR_COST":
                result["BASE_SALARY_COST"],
            "TOTAL_LABOR_COST": round(
                stats.total_labor_cost,
                2
            ),
            "TOTAL_OVERTIME_EXTRA_COST":
                result["OVERTIME_COST"],
            "OVERTIME_PERCENT":
                result["OVERTIME_PERCENTAGE"],
            "TOTAL_ADMITTED": result["ADMITTED_EQUIPMENT"],
            "TOTAL_REJECTED": result["BLOCKED_ARRIVALS"],
            "MAX_STORAGE_INVENTORY":
                result["MAX_PHYSICAL_DEPOT_OCCUPANCY"],
            "CAPACITY_VIOLATIONS": stats.capacity_violations,
            "CAPACITY_OK": (
                result["MAX_PHYSICAL_DEPOT_OCCUPANCY"]
                <= self.config.inventory_capacity
                and stats.capacity_violations == 0
            ),
            "STORAGE_INVENTORY_HISTORY":
                result["PHYSICAL_DEPOT_HISTORY"],
            "ADMITTED_HISTORY":
                result["ADMITTED_DAILY_HISTORY"],
            "REJECTED_HISTORY":
                result["BLOCKED_DAILY_HISTORY"],
        })
