from dataclasses import asdict, is_dataclass

import pandas as pd


CSV_SEPARATOR = ";"
CSV_DECIMAL = ","
LIST_SEPARATOR = " | "


PERCENT_CONFIG_COLUMNS = {
    "threshold_percentage": "PARAM_THRESHOLD_PERCENTAGE_PCT",
    "max_blocked_percentage": "PARAM_MAX_BLOCKED_PERCENTAGE_PCT",
    "max_overtime_percentage": "PARAM_MAX_OVERTIME_PERCENTAGE_PCT",
    "minimum_acceptance_rate": "PARAM_MINIMUM_ACCEPTANCE_RATE_PCT",
}


RUN_METRIC_COLUMNS = {
    "CRT_PROCESSED": "CRT_PROCESSED",
    "LCD_PROCESSED": "LCD_PROCESSED",
    "IRRECOVERABLE_PROCESSED": "IRRECOVERABLE_PROCESSED",
    "TOTAL_PROCESSED": "TOTAL_PROCESSED",
    "TOTAL_COST": "TOTAL_COST",
    "CRT_LCD_PROCESSING_COST": "CRT_LCD_PROCESSING_COST",
    "BASE_SALARY_COST": "BASE_SALARY_COST",
    "OVERTIME_COST": "OVERTIME_COST",
    "FINAL_TOTAL_INVENTORY": "FINAL_TOTAL_INVENTORY",
    "FINAL_PHYSICAL_DEPOT_INVENTORY":
        "FINAL_PHYSICAL_DEPOT_INVENTORY",
    "AVERAGE_SYSTEM_INVENTORY": "AVERAGE_SYSTEM_INVENTORY",
    "TOTAL_ARRIVALS": "TOTAL_ARRIVALS",
    "ADMITTED_EQUIPMENT": "ADMITTED_EQUIPMENT",
    "BLOCKED_ARRIVALS": "BLOCKED_ARRIVALS",
    "BLOCKED_PERCENTAGE": "BLOCKED_PERCENTAGE_PCT",
    "MAX_PHYSICAL_DEPOT_OCCUPANCY":
        "MAX_PHYSICAL_DEPOT_OCCUPANCY",
    "OVERTIME_DAYS_USED": "OVERTIME_DAYS_USED",
    "OVERTIME_PERCENTAGE": "OVERTIME_PERCENTAGE_PCT",
    "VIOLATION_COUNT": "VIOLATION_COUNT",
}


SUMMARY_METRIC_COLUMNS = {
    "BLOCKED_PERCENTAGE": "BLOCKED_PERCENTAGE_PCT",
    "OVERTIME_PERCENTAGE": "OVERTIME_PERCENTAGE_PCT",
}


def build_export_dataframes(experiment_results):

    scenario_id = experiment_results["SCENARIO_ID"]
    executed_at = experiment_results["EXECUTED_AT"]
    model_version = experiment_results["MODEL_VERSION"]
    config_snapshot = experiment_results["CONFIG"]

    return {
        "runs": build_runs_dataframe(
            experiment_results["RUN_RESULTS"],
            config_snapshot,
            scenario_id,
            executed_at,
            model_version
        ),
        "daily_history": build_daily_history_dataframe(
            experiment_results["RUN_RESULTS"],
            scenario_id,
            executed_at,
            model_version
        ),
        "summary": build_summary_dataframe(
            experiment_results["AGGREGATED_RESULTS"],
            experiment_results["ACCEPTANCE_SUMMARY"],
            scenario_id,
            executed_at,
            model_version
        ),
    }


def build_runs_dataframe(
    run_results,
    config,
    scenario_id,
    executed_at,
    model_version="1.0"
):

    config_dict = _config_to_dict(config)
    rows = []

    for result in run_results:

        row = {
            "SCENARIO_ID": scenario_id,
            "EXECUTED_AT": executed_at,
            "MODEL_VERSION": model_version,
            "RUNS_REQUESTED": config_dict.get("runs"),
            "BASE_SEED": config_dict.get("base_seed"),
            "RUN_ID": result["RUN_ID"],
            "SEED": result["SEED"],
            "IS_ACCEPTED": result["IS_ACCEPTED"],
            "REJECTION_REASONS": _join_list(
                result.get("REJECTION_REASONS", [])
            ),
        }

        row.update(
            _build_parameter_columns(config_dict)
        )

        for result_key, column_name in RUN_METRIC_COLUMNS.items():
            row[column_name] = result[result_key]

        row["VIOLATIONS"] = _join_list(
            result.get("VIOLATIONS", [])
        )

        rows.append(row)

    return pd.DataFrame(rows)


def build_daily_history_dataframe(
    run_results,
    scenario_id,
    executed_at,
    model_version="1.0"
):

    rows = []

    for result in run_results:

        histories = {
            "DAYS": result["DAYS"],
            "PHYSICAL_DEPOT_INVENTORY":
                result["PHYSICAL_DEPOT_HISTORY"],
            "TOTAL_SYSTEM_INVENTORY":
                result["INVENTORY_HISTORY"],
            "ADMITTED_EQUIPMENT_DAILY":
                result["ADMITTED_DAILY_HISTORY"],
            "BLOCKED_EQUIPMENT_DAILY":
                result["BLOCKED_DAILY_HISTORY"],
            "CRT_PROCESSED_CUMULATIVE":
                result["CRT_HISTORY"],
            "LCD_PROCESSED_CUMULATIVE":
                result["LCD_HISTORY"],
            "IRRECOVERABLE_PROCESSED_CUMULATIVE":
                result["IRRECOVERABLE_HISTORY"],
            "COST_CUMULATIVE":
                result["COST_HISTORY"],
            "DAILY_OVERTIME_EXTRA_COST":
                result["DAILY_OVERTIME_EXTRA_COST_HISTORY"],
            "OVERTIME_ACTIVE_TODAY":
                result.get(
                    "OVERTIME_ACTIVE_DAILY_HISTORY",
                    [
                        cost > 0
                        for cost in result[
                            "DAILY_OVERTIME_EXTRA_COST_HISTORY"
                        ]
                    ]
                ),
            "OVERTIME_SCHEDULED_FOR_NEXT_DAY":
                result.get(
                    "OVERTIME_SCHEDULED_NEXT_DAY_HISTORY",
                    [False] * len(result["DAYS"])
                ),
            "CRITICAL_THRESHOLD_UNITS":
                result.get(
                    "OVERTIME_CRITICAL_THRESHOLD_HISTORY",
                    [
                        result.get("CRITICAL_THRESHOLD_UNITS")
                    ] * len(result["DAYS"])
                ),
        }

        history_length = min(
            len(values)
            for values in histories.values()
        )

        for index in range(history_length):

            crt_processed = histories[
                "CRT_PROCESSED_CUMULATIVE"
            ][index]
            lcd_processed = histories[
                "LCD_PROCESSED_CUMULATIVE"
            ][index]
            irrecoverable_processed = histories[
                "IRRECOVERABLE_PROCESSED_CUMULATIVE"
            ][index]
            physical_inventory = histories[
                "PHYSICAL_DEPOT_INVENTORY"
            ][index]
            overtime_scheduled = histories[
                "OVERTIME_SCHEDULED_FOR_NEXT_DAY"
            ][index]

            rows.append({
                "SCENARIO_ID": scenario_id,
                "EXECUTED_AT": executed_at,
                "MODEL_VERSION": model_version,
                "RUN_ID": result["RUN_ID"],
                "SEED": result["SEED"],
                "DAY": histories["DAYS"][index],
                "PHYSICAL_DEPOT_INVENTORY":
                    physical_inventory,
                "TOTAL_SYSTEM_INVENTORY":
                    histories["TOTAL_SYSTEM_INVENTORY"][index],
                "CRITICAL_THRESHOLD_UNITS":
                    histories["CRITICAL_THRESHOLD_UNITS"][index],
                "OVERTIME_TRIGGER_PHYSICAL_INVENTORY":
                    physical_inventory,
                "OVERTIME_TRIGGER_REACHED_THRESHOLD":
                    overtime_scheduled,
                "PREVIOUS_DAY_PHYSICAL_DEPOT_INVENTORY": (
                    None
                    if index == 0
                    else histories["PHYSICAL_DEPOT_INVENTORY"][index - 1]
                ),
                "PREVIOUS_DAY_REACHED_THRESHOLD": (
                    None
                    if index == 0
                    else histories[
                        "OVERTIME_SCHEDULED_FOR_NEXT_DAY"
                    ][index - 1]
                ),
                "ADMITTED_EQUIPMENT_DAILY":
                    histories["ADMITTED_EQUIPMENT_DAILY"][index],
                "BLOCKED_EQUIPMENT_DAILY":
                    histories["BLOCKED_EQUIPMENT_DAILY"][index],
                "CRT_PROCESSED_CUMULATIVE": crt_processed,
                "LCD_PROCESSED_CUMULATIVE": lcd_processed,
                "IRRECOVERABLE_PROCESSED_CUMULATIVE":
                    irrecoverable_processed,
                "TOTAL_PROCESSED_CUMULATIVE": (
                    crt_processed
                    + lcd_processed
                    + irrecoverable_processed
                ),
                "COST_CUMULATIVE":
                    histories["COST_CUMULATIVE"][index],
                "DAILY_OVERTIME_EXTRA_COST":
                    histories["DAILY_OVERTIME_EXTRA_COST"][index],
                "OVERTIME_ACTIVE_TODAY":
                    histories["OVERTIME_ACTIVE_TODAY"][index],
                "OVERTIME_SCHEDULED_FOR_NEXT_DAY":
                    overtime_scheduled,
                "OVERTIME_USED": (
                    histories["OVERTIME_ACTIVE_TODAY"][index]
                ),
            })

    return pd.DataFrame(rows)


def build_summary_dataframe(
    aggregated_results,
    acceptance_summary,
    scenario_id,
    executed_at,
    model_version="1.0"
):

    rows = []

    for metric_name, metric_summary in (
        aggregated_results["METRICS"].items()
    ):
        rows.append(
            _summary_row(
                scenario_id,
                executed_at,
                model_version,
                "METRIC",
                SUMMARY_METRIC_COLUMNS.get(
                    metric_name,
                    metric_name
                ),
                mean=metric_summary["MEAN"],
                minimum=metric_summary["MIN"],
                maximum=metric_summary["MAX"],
                std=metric_summary["STD"],
            )
        )

    acceptance_rows = {
        "RUNS_EXECUTED": acceptance_summary["RUNS_EXECUTED"],
        "RUNS_ACCEPTED": acceptance_summary["ACCEPTED_RUNS"],
        "RUNS_REJECTED": acceptance_summary["REJECTED_RUNS"],
        "ACCEPTANCE_RATE_PCT":
            acceptance_summary["ACCEPTANCE_RATE"],
        "MINIMUM_ACCEPTANCE_RATE_PCT":
            acceptance_summary["MINIMUM_ACCEPTANCE_RATE"],
        "SCENARIO_IS_ACCEPTED":
            acceptance_summary["IS_SCENARIO_ACCEPTED"],
    }

    for metric_name, value in acceptance_rows.items():
        rows.append(
            _summary_row(
                scenario_id,
                executed_at,
                model_version,
                "ACCEPTANCE",
                metric_name,
                value=value
            )
        )

    for reason_summary in acceptance_summary[
        "REJECTION_REASON_SUMMARY"
    ]:
        reason = reason_summary["REASON"]
        rows.append(
            _summary_row(
                scenario_id,
                executed_at,
                model_version,
                "REJECTION_REASON",
                f"RUNS_AFFECTED | {reason}",
                value=reason_summary["RUNS_AFFECTED"]
            )
        )
        rows.append(
            _summary_row(
                scenario_id,
                executed_at,
                model_version,
                "REJECTION_REASON",
                f"PERCENTAGE_PCT | {reason}",
                value=reason_summary["PERCENTAGE"]
            )
        )

    return pd.DataFrame(rows)


def dataframe_to_csv_bytes(df):

    return df.to_csv(
        index=False,
        sep=CSV_SEPARATOR,
        decimal=CSV_DECIMAL,
        lineterminator="\n"
    ).encode("utf-8-sig")


def _config_to_dict(config):

    if is_dataclass(config):
        return asdict(config)

    return dict(config)


def _build_parameter_columns(config_dict):

    row = {}

    for key, value in config_dict.items():

        if key in PERCENT_CONFIG_COLUMNS:
            row[PERCENT_CONFIG_COLUMNS[key]] = (
                None
                if value is None
                else value * 100
            )
            continue

        row[f"PARAM_{key.upper()}"] = value

    return row


def _summary_row(
    scenario_id,
    executed_at,
    model_version,
    section,
    metric,
    mean=None,
    minimum=None,
    maximum=None,
    std=None,
    value=None
):

    return {
        "SCENARIO_ID": scenario_id,
        "EXECUTED_AT": executed_at,
        "MODEL_VERSION": model_version,
        "SECTION": section,
        "METRIC": metric,
        "MEAN": mean,
        "MIN": minimum,
        "MAX": maximum,
        "STD": std,
        "VALUE": value,
    }


def _join_list(values):

    return LIST_SEPARATOR.join(
        str(value)
        for value in values
    )
