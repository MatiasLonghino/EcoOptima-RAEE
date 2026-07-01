import pandas as pd
import streamlit as st


METRIC_LABELS = [
    ("CRT_PROCESSED", "CRT procesados"),
    ("LCD_PROCESSED", "LCD/LED procesados"),
    ("IRRECOVERABLE_PROCESSED", "Irrecuperables procesados"),
    ("TOTAL_PROCESSED", "Total procesado"),
    ("TOTAL_COST", "Costo total"),
    ("CRT_LCD_PROCESSING_COST", "Costo procesamiento CRT/LCD"),
    ("BASE_SALARY_COST", "Sueldos base"),
    ("OVERTIME_COST", "Extra por horas extra"),
    ("FINAL_TOTAL_INVENTORY", "Inventario total final"),
    ("FINAL_PHYSICAL_DEPOT_INVENTORY", "Deposito fisico final"),
    ("AVERAGE_SYSTEM_INVENTORY", "Inventario promedio en sistema"),
    ("TOTAL_ARRIVALS", "Equipos llegados"),
    ("ADMITTED_EQUIPMENT", "Equipos admitidos"),
    ("BLOCKED_ARRIVALS", "Ingresos bloqueados"),
    ("BLOCKED_PERCENTAGE", "Porcentaje de bloqueos"),
    ("MAX_PHYSICAL_DEPOT_OCCUPANCY", "Maximo en deposito fisico"),
    ("VIOLATION_COUNT", "Violaciones detectadas"),
    ("OVERTIME_PERCENTAGE", "Porcentaje de horas extra"),
]


def show_results(results):
    """
    Muestra los resultados agregados de todas las corridas.
    """

    run_results = results["RUN_RESULTS"]
    aggregated_results = results["AGGREGATED_RESULTS"]
    acceptance_summary = results["ACCEPTANCE_SUMMARY"]

    st.subheader("Resumen de aceptacion")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Corridas ejecutadas",
            acceptance_summary["RUNS_EXECUTED"]
        )

    with col2:
        st.metric(
            "Aceptables",
            acceptance_summary["ACCEPTED_RUNS"]
        )

    with col3:
        st.metric(
            "Rechazadas",
            acceptance_summary["REJECTED_RUNS"]
        )

    with col4:
        st.metric(
            "Tasa de aceptacion",
            f"{acceptance_summary['ACCEPTANCE_RATE']:.2f}%"
        )

    with col5:
        st.metric(
            "Minimo requerido",
            f"{acceptance_summary['MINIMUM_ACCEPTANCE_RATE']:.2f}%"
        )

    if acceptance_summary["IS_SCENARIO_ACCEPTED"]:
        st.success(
            "Escenario aceptable: alcanza la tasa minima configurada."
        )
    else:
        st.error(
            "Escenario no aceptable: no alcanza la tasa minima configurada."
        )

    _show_rejection_reasons(
        acceptance_summary
    )

    st.subheader("Metricas agregadas")

    st.dataframe(
        _build_metrics_dataframe(
            aggregated_results["METRICS"]
        ),
        use_container_width=True,
        hide_index=True
    )

    with st.expander("Detalle por corrida"):
        st.dataframe(
            _build_run_detail_dataframe(
                run_results
            ),
            use_container_width=True,
            hide_index=True
        )

    with st.expander("Detalle diario por corrida"):
        st.dataframe(
            _build_daily_detail_dataframe(
                run_results
            ),
            use_container_width=True,
            hide_index=True
        )


def _show_rejection_reasons(acceptance_summary):

    reason_summary = acceptance_summary[
        "REJECTION_REASON_SUMMARY"
    ]

    if not reason_summary:
        st.info(
            "No se registraron causas de rechazo."
        )
        return

    df = pd.DataFrame(reason_summary).rename(
        columns={
            "REASON": "Motivo",
            "RUNS_AFFECTED": "Corridas afectadas",
            "PERCENTAGE": "Porcentaje",
        }
    )

    st.markdown("#### Causas de rechazo")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


def _build_metrics_dataframe(metrics):

    rows = []

    for metric_key, metric_label in METRIC_LABELS:

        if metric_key not in metrics:
            continue

        summary = metrics[metric_key]

        rows.append({
            "Metrica": metric_label,
            "Promedio": summary["MEAN"],
            "Minimo": summary["MIN"],
            "Maximo": summary["MAX"],
            "Desvio estandar": summary["STD"],
        })

    return pd.DataFrame(rows)


def _build_run_detail_dataframe(run_results):

    rows = []

    for result in run_results:

        rejection_reasons = "; ".join(
            result["REJECTION_REASONS"]
        )

        rows.append({
            "Corrida": result["RUN_ID"],
            "Semilla": result["SEED"],
            "Aceptable": "Si" if result["IS_ACCEPTED"] else "No",
            "CRT": result["CRT_PROCESSED"],
            "LCD/LED": result["LCD_PROCESSED"],
            "Irrecuperables": result["IRRECOVERABLE_PROCESSED"],
            "Inventario final": result["FINAL_TOTAL_INVENTORY"],
            "Costo total": result["TOTAL_COST"],
            "Bloqueados": result["BLOCKED_ARRIVALS"],
            "Horas extra": result["OVERTIME_PERCENTAGE"],
            "Motivos de rechazo": rejection_reasons or "-",
        })

    return pd.DataFrame(rows)


def _build_daily_detail_dataframe(run_results):

    rows = []

    for result in run_results:

        days = result["DAYS"]
        physical_history = result["PHYSICAL_DEPOT_HISTORY"]
        system_history = result["INVENTORY_HISTORY"]
        active_history = result.get(
            "OVERTIME_ACTIVE_DAILY_HISTORY",
            [False] * len(days)
        )
        scheduled_history = result.get(
            "OVERTIME_SCHEDULED_NEXT_DAY_HISTORY",
            [False] * len(days)
        )
        threshold_history = result.get(
            "OVERTIME_CRITICAL_THRESHOLD_HISTORY",
            [
                result.get("CRITICAL_THRESHOLD_UNITS")
            ] * len(days)
        )
        overtime_cost_history = result.get(
            "DAILY_OVERTIME_EXTRA_COST_HISTORY",
            [0] * len(days)
        )

        history_length = min(
            len(days),
            len(physical_history),
            len(system_history),
            len(active_history),
            len(scheduled_history),
            len(threshold_history),
            len(overtime_cost_history)
        )

        for index in range(history_length):

            rows.append({
                "Corrida": result["RUN_ID"],
                "Semilla": result["SEED"],
                "Dia": days[index],
                "Inventario fisico cierre":
                    physical_history[index],
                "Inventario sistema cierre":
                    system_history[index],
                "Umbral critico":
                    threshold_history[index],
                "Turno extra activo":
                    "Si" if active_history[index] else "No",
                "Programa turno siguiente":
                    "Si" if scheduled_history[index] else "No",
                "Costo extra diario":
                    overtime_cost_history[index],
            })

    return pd.DataFrame(rows)
