import streamlit as st


def show_results(results):

    st.subheader(
        "Resultados"
    )

    st.metric(
        "CRT Procesados",
        results["CRT"]
    )

    st.metric(
        "LCD Procesados",
        results["LCD"]
    )

    st.metric(
        "Irrecuperables",
        results["IRRECOVERABLE"]
    )

    st.metric(
        "Inventario Final",
        results["FINAL_INVENTORY"]
    )

    st.metric(
        "Inventario Promedio",
        results["AVG_INVENTORY"]
    )

    st.metric(
        "Costo Total",
        results["TOTAL_COST"]
    )

    st.metric(
        "% Días con Horas Extra",
        results["OVERTIME_PERCENT"]
    )