import streamlit as st


def show_results(results):
    """
    Muestra los resultados principales de la simulacion.

    Separa los resultados operativos, los costos y los
    indicadores especificos de capacidad del deposito.
    """

    st.subheader("Resultados principales")

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
            "LCD/LED procesados",
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
            "% dias con horas extra",
            f"{results['OVERTIME_PERCENT']:.2f}%"
        )

    st.subheader("Desglose de costos")

    col_cost1, col_cost2, col_cost3 = st.columns(3)

    with col_cost1:
        st.metric(
            "Procesamiento CRT/LCD",
            f"${results['TOTAL_PROCESSING_COST']:,.0f}"
        )

    with col_cost2:
        st.metric(
            "Sueldos base",
            f"${results['TOTAL_BASE_LABOR_COST']:,.0f}"
        )

    with col_cost3:
        st.metric(
            "Extra por horas extra",
            f"${results['TOTAL_OVERTIME_EXTRA_COST']:,.0f}"
        )

    st.caption(
        "El costo total suma procesamiento, sueldos base y el "
        "recargo aplicado en los dias con turnos extra."
    )

    st.subheader("Inventario del sistema")

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "Inventario total final",
            results["FINAL_INVENTORY"]
        )

    with col8:
        st.metric(
            "Deposito fisico final",
            results["FINAL_STORAGE_INVENTORY"]
        )

    with col9:
        st.metric(
            "Inventario promedio en sistema",
            f"{results['AVG_INVENTORY']:.2f}"
        )

    st.caption(
        "El inventario total incluye el deposito y las colas de "
        "procesamiento CRT/LCD. El deposito fisico solo incluye "
        "los equipos realmente almacenados."
    )

    st.subheader("Control de capacidad")

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
            "Maximo en deposito",
            results["MAX_STORAGE_INVENTORY"]
        )

    with col13:
        st.metric(
            "Violaciones detectadas",
            results["CAPACITY_VIOLATIONS"]
        )

    if results["CAPACITY_OK"]:
        st.success(
            "Restriccion de capacidad cumplida: el inventario "
            "fisico nunca supero el limite del deposito."
        )
    else:
        st.error(
            "Se detecto una violacion de capacidad. Revisa la "
            "logica de admision al deposito."
        )
