import pandas as pd
import streamlit as st
import altair as alt


def inventory_chart(results):
    """
    Grafica la evolución del inventario total en depósito
    a lo largo de los días simulados.

    Incluye:
    - línea horizontal de capacidad máxima
    - línea horizontal de umbral crítico
    """

    days = results["DAYS"]
    inventory_history = results["INVENTORY_HISTORY"]

    inventory_capacity = results["INVENTORY_CAPACITY"]
    critical_threshold = results["CRITICAL_THRESHOLD"]

    min_length = min(
        len(days),
        len(inventory_history)
    )

    df_inventory = pd.DataFrame({
        "Día": days[:min_length],
        "Unidades en depósito": inventory_history[:min_length]
    })

    st.subheader("📈 Evolución del inventario en depósito")

    inventory_line = alt.Chart(df_inventory).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Día:Q",
            title="Día"
        ),
        y=alt.Y(
            "Unidades en depósito:Q",
            title="Unidades en depósito"
        ),
        tooltip=[
            "Día",
            "Unidades en depósito"
        ]
    )

    capacity_line = alt.Chart(
        pd.DataFrame({
            "Valor": [inventory_capacity],
            "Referencia": [
                f"Capacidad máxima ({inventory_capacity})"
            ]
        })
    ).mark_rule(
        color="red",
        strokeWidth=3
    ).encode(
        y="Valor:Q",
        tooltip=[
            "Referencia",
            "Valor"
        ]
    )

    threshold_line = alt.Chart(
        pd.DataFrame({
            "Valor": [critical_threshold],
            "Referencia": [
                f"Umbral crítico ({critical_threshold:.0f})"
            ]
        })
    ).mark_rule(
        color="orange",
        strokeDash=[8, 4],
        strokeWidth=3
    ).encode(
        y="Valor:Q",
        tooltip=[
            "Referencia",
            "Valor"
        ]
    )

    chart = (
        inventory_line
        + capacity_line
        + threshold_line
    ).properties(
        height=400
    ).interactive()

    st.altair_chart(
        chart,
        use_container_width=True
    )

    st.caption(
        f"Capacidad máxima: {inventory_capacity} unidades | "
        f"Umbral crítico: {critical_threshold:.0f} unidades"
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