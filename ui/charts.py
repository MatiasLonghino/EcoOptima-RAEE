import altair as alt
import pandas as pd
import streamlit as st


def inventory_chart(results, config):
    """
    Grafica el inventario físico dentro del depósito.

    Este valor no incluye las colas de CRT ni LCD, porque esas
    unidades ya no están físicamente almacenadas en el depósito.

    Incluye líneas de referencia para:
    - Capacidad máxima del depósito.
    - Umbral que activa horas extra.
    """

    days = results["DAYS"]

    storage_inventory_history = results[
        "STORAGE_INVENTORY_HISTORY"
    ]

    min_length = min(
        len(days),
        len(storage_inventory_history)
    )

    if min_length == 0:
        st.info("No hay datos de inventario para graficar.")
        return

    capacity = config.inventory_capacity

    threshold = (
        config.inventory_capacity
        * config.threshold_percentage
    )

    df = pd.DataFrame({
        "Día": days[:min_length],
        "Inventario físico": storage_inventory_history[:min_length]
    })

    limits_df = pd.DataFrame({
        "Valor": [
            capacity,
            threshold
        ],
        "Límite": [
            "Capacidad máxima",
            "Umbral de horas extra"
        ]
    })

    max_value = max(
        capacity,
        df["Inventario físico"].max()
    )

    y_encoding = alt.Y(
        "Valor:Q",
        title="Equipos",
        scale=alt.Scale(
            domain=[
                0,
                max_value * 1.10
            ]
        )
    )

    inventory_line = (
        alt.Chart(
            df.rename(
                columns={
                    "Inventario físico": "Valor"
                }
            )
        )
        .mark_line(
            point=True
        )
        .encode(
            x=alt.X(
                "Día:Q",
                title="Día",
                axis=alt.Axis(
                    tickMinStep=1
                )
            ),
            y=y_encoding,
            tooltip=[
                alt.Tooltip(
                    "Día:Q",
                    title="Día"
                ),
                alt.Tooltip(
                    "Valor:Q",
                    title="Inventario físico"
                )
            ]
        )
    )

    capacity_line = (
        alt.Chart(
            limits_df[
                limits_df["Límite"]
                == "Capacidad máxima"
            ]
        )
        .mark_rule(
            color="#e45756",
            strokeWidth=2,
            strokeDash=[6, 4]
        )
        .encode(
            y=y_encoding,
            tooltip=[
                alt.Tooltip(
                    "Límite:N"
                ),
                alt.Tooltip(
                    "Valor:Q",
                    title="Equipos"
                )
            ]
        )
    )

    threshold_line = (
        alt.Chart(
            limits_df[
                limits_df["Límite"]
                == "Umbral de horas extra"
            ]
        )
        .mark_rule(
            color="#f2a900",
            strokeWidth=2,
            strokeDash=[4, 4]
        )
        .encode(
            y=y_encoding,
            tooltip=[
                alt.Tooltip(
                    "Límite:N"
                ),
                alt.Tooltip(
                    "Valor:Q",
                    title="Equipos"
                )
            ]
        )
    )

    chart = (
        inventory_line
        + capacity_line
        + threshold_line
    ).properties(
        height=340
    )

    st.subheader("📈 Inventario físico del depósito")

    st.altair_chart(
        chart,
        use_container_width=True
    )

    st.caption(
        f"Línea roja: capacidad máxima ({capacity} equipos). "
        f"Línea amarilla: umbral de horas extra "
        f"({threshold:.0f} equipos)."
    )


def admission_chart(results):
    """
    Grafica los equipos admitidos y bloqueados por falta
    de espacio en el depósito.
    """

    days = results["DAYS"]

    admitted_history = results["ADMITTED_HISTORY"]
    rejected_history = results["REJECTED_HISTORY"]

    min_length = min(
        len(days),
        len(admitted_history),
        len(rejected_history)
    )

    if min_length == 0:
        st.info("No hay datos de admisión para graficar.")
        return

    df = pd.DataFrame({
        "Día": days[:min_length],
        "Equipos admitidos": admitted_history[:min_length],
        "Equipos bloqueados": rejected_history[:min_length]
    })

    st.subheader("🚚 Admisión diaria de equipos")

    st.bar_chart(
        df,
        x="Día",
        y=[
            "Equipos admitidos",
            "Equipos bloqueados"
        ],
        use_container_width=True
    )

    st.caption(
        "Los equipos bloqueados representan ingresos que no pudieron "
        "entrar porque el depósito no tenía espacio disponible."
    )


def processed_chart(results):
    """
    Grafica la evolución acumulada de unidades procesadas,
    discriminadas por tipo: CRT, LCD e irrecuperables.
    """

    days = results["DAYS"]
    crt_history = results["CRT_HISTORY"]
    lcd_history = results["LCD_HISTORY"]
    irrecoverable_history = results["IRRECOVERABLE_HISTORY"]

    min_length = min(
        len(days),
        len(crt_history),
        len(lcd_history),
        len(irrecoverable_history)
    )

    if min_length == 0:
        st.info("No hay datos de procesamiento para graficar.")
        return

    df = pd.DataFrame({
        "Día": days[:min_length],
        "CRT procesados": crt_history[:min_length],
        "LCD procesados": lcd_history[:min_length],
        "Irrecuperables procesados": irrecoverable_history[:min_length]
    })

    st.subheader("📦 Unidades procesadas acumuladas por tipo")

    st.line_chart(
        df,
        x="Día",
        y=[
            "CRT procesados",
            "LCD procesados",
            "Irrecuperables procesados"
        ],
        use_container_width=True
    )


def cost_chart(results):
    """
    Grafica la evolución del costo total acumulado
    durante la simulación.
    """

    days = results["DAYS"]
    cost_history = results["COST_HISTORY"]

    min_length = min(
        len(days),
        len(cost_history)
    )

    if min_length == 0:
        st.info("No hay datos de costo para graficar.")
        return

    df = pd.DataFrame({
        "Día": days[:min_length],
        "Costo acumulado": cost_history[:min_length]
    })

    st.subheader("💰 Evolución del costo acumulado")

    st.line_chart(
        df,
        x="Día",
        y="Costo acumulado",
        use_container_width=True
    )