import pandas as pd
import streamlit as st


def inventory_chart(results):
    """
    Grafica la evolución del inventario total en depósito
    a lo largo de los días simulados.
    """

    days = results["DAYS"]
    inventory_history = results["INVENTORY_HISTORY"]

    min_length = min(
        len(days),
        len(inventory_history)
    )

    df = pd.DataFrame({
        "Día": days[:min_length],
        "Unidades en depósito": inventory_history[:min_length]
    })

    st.subheader("Evolución del inventario en depósito")

    st.line_chart(
        df,
        x="Día",
        y="Unidades en depósito"
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

    st.subheader("Unidades procesadas acumuladas por tipo")

    st.line_chart(
        df,
        x="Día",
        y=[
            "CRT procesados",
            "LCD procesados",
            "Irrecuperables procesados"
        ]
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

    st.subheader("Evolución del costo acumulado")

    st.line_chart(
        df,
        x="Día",
        y="Costo acumulado"
    )