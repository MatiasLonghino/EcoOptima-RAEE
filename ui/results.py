import streamlit as st


def show_results(results):
    """
    Muestra los resultados principales de la simulación.

    Separa los resultados operativos generales de los
    indicadores específicos de capacidad del depósito.
    """

    st.subheader("📊 Resultados principales")

    total_processed = (
        results["CRT"]
        + results["LCD"]
        + results["IRRECOVERABLE"]
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "CRT procesados",
            results["CRT"]
        )

    with col2:
        st.metric(
            "LCD procesados",
            results["LCD"]
        )

    with col3:
        st.metric(
            "Irrecuperables",
            results["IRRECOVERABLE"]
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "Total procesado",
            total_processed
        )

    with col5:
        st.metric(
            "Costo total",
            f"${results['TOTAL_COST']:,.0f}"
        )

    with col6:
        st.metric(
            "% días con horas extra",
            f"{results['OVERTIME_PERCENT']:.2f}%"
        )

    st.subheader("📦 Inventario del sistema")

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "Inventario total final",
            results["FINAL_INVENTORY"]
        )

    with col8:
        st.metric(
            "Depósito físico final",
            results["FINAL_STORAGE_INVENTORY"]
        )

    with col9:
        st.metric(
            "Inventario promedio en sistema",
            f"{results['AVG_INVENTORY']:.2f}"
        )

    st.caption(
        "El inventario total incluye el depósito y las colas de "
        "procesamiento CRT/LCD. El depósito físico solo incluye "
        "los equipos realmente almacenados."
    )

    st.subheader("🛡️ Control de capacidad")

    col10, col11, col12, col13 = st.columns(4)

    with col10:
        st.metric(
            "Equipos admitidos",
            results["TOTAL_ADMITTED"]
        )

    with col11:
        st.metric(
            "Ingresos bloqueados",
            results["TOTAL_REJECTED"]
        )

    with col12:
        st.metric(
            "Máximo en depósito",
            results["MAX_STORAGE_INVENTORY"]
        )

    with col13:
        st.metric(
            "Violaciones detectadas",
            results["CAPACITY_VIOLATIONS"]
        )

    if results["CAPACITY_OK"]:
        st.success(
            "✅ Restricción de capacidad cumplida: el inventario "
            "físico nunca superó el límite del depósito."
        )
    else:
        st.error(
            "❌ Se detectó una violación de capacidad. Revisá la "
            "lógica de admisión al depósito."
        )