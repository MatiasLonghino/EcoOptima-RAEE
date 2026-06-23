import streamlit as st

from simulation.config import SimulationConfig


def build_sidebar():
    """
    Construye el panel lateral con los parametros que puede
    modificar el usuario.

    El resto de los valores del modelo se toman como datos fijos
    desde SimulationConfig.
    """

    with st.sidebar:
        st.title("Parametros")

        st.markdown("### Inventario")

        inventory_capacity = st.number_input(
            "Capacidad maxima del deposito",
            min_value=1,
            value=SimulationConfig.inventory_capacity,
            step=10
        )

        threshold_percentage = st.slider(
            "Umbral critico de ocupacion",
            min_value=0.50,
            max_value=1.00,
            value=SimulationConfig.threshold_percentage,
            step=0.01
        )

        initial_inventory_default = min(
            SimulationConfig.initial_inventory,
            inventory_capacity
        )

        initial_inventory = st.number_input(
            "Stock inicial",
            min_value=0,
            max_value=inventory_capacity,
            value=initial_inventory_default,
            step=1
        )

        st.divider()

        st.markdown("### Llegadas")

        arrival_lambda = st.number_input(
            "Llegadas promedio por dia",
            min_value=0,
            value=SimulationConfig.arrival_lambda,
            step=1
        )

        st.divider()

        st.markdown("### Servidores")

        triage_servers = st.number_input(
            "Cantidad de servidores de triage",
            min_value=1,
            value=SimulationConfig.triage_servers,
            step=1
        )

        crt_servers = st.number_input(
            "Cantidad de servidores CRT",
            min_value=1,
            value=SimulationConfig.crt_servers,
            step=1
        )

        lcd_servers = st.number_input(
            "Cantidad de servidores LCD/LED",
            min_value=1,
            value=SimulationConfig.lcd_servers,
            step=1
        )

        st.divider()

        st.markdown("### Tiempo de simulacion")

        days = st.number_input(
            "Dias simulados",
            min_value=1,
            value=SimulationConfig.days,
            step=1
        )

    return SimulationConfig(
        days=days,
        inventory_capacity=inventory_capacity,
        threshold_percentage=threshold_percentage,
        initial_inventory=initial_inventory,
        arrival_lambda=arrival_lambda,
        triage_servers=triage_servers,
        crt_servers=crt_servers,
        lcd_servers=lcd_servers
    )
