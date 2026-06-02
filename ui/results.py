import streamlit as st


def show_results(results):
    """
    Muestra los resultados principales de la simulación.

    En vez de mostrar las métricas una debajo de la otra,
    se organizan en columnas para ahorrar espacio y mejorar
    la lectura visual del dashboard.
    """

    st.subheader("📊 Resultados principales")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "CRT procesados",
            results["CRT"]
        )

        st.metric(
            "Inventario final",
            results["FINAL_INVENTORY"]
        )

    with col2:
        st.metric(
            "LCD procesados",
            results["LCD"]
        )

        st.metric(
            "Inventario promedio",
            round(results["AVG_INVENTORY"], 2)
        )

    with col3:
        st.metric(
            "Irrecuperables",
            results["IRRECOVERABLE"]
        )

        st.metric(
            "Costo total",
            f"${results['TOTAL_COST']:,.0f}"
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "% días con horas extra",
            f"{results['OVERTIME_PERCENT']:.2f}%"
        )

    with col5:
        total_processed = (
            results["CRT"]
            + results["LCD"]
            + results["IRRECOVERABLE"]
        )

        st.metric(
            "Total procesado",
            total_processed
        )

    with col6:
        st.metric(
            "Unidades en sistema",
            results["FINAL_INVENTORY"]
        )

    mean_test = results["MEAN_TEST"]

    st.subheader("🧪 Prueba de los promedios")

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "Promedio muestral",
            f"{mean_test['SAMPLE_MEAN']:.4f}"
        )

    with col8:
        st.metric(
            "Z calculado",
            f"{mean_test['Z_STATISTIC']:.4f}"
        )

    with col9:
        st.metric(
            "Z crítico",
            f"{mean_test['CRITICAL_VALUE']:.4f}"
        )

    if mean_test["REJECT_NULL"]:
        st.error(
            f"{mean_test['DECISION']}: el generador no pasa la prueba con α = {mean_test['ALPHA']}."
        )
    else:
        st.success(
            f"{mean_test['DECISION']}: el generador pasa la prueba con α = {mean_test['ALPHA']}."
        )