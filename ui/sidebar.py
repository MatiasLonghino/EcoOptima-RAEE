import streamlit as st

from simulation.config import SimulationConfig


def build_sidebar():

    st.sidebar.header(
        "Parámetros"
    )

    return SimulationConfig(

        threshold_percentage=
        st.sidebar.slider(
            "Umbral",
            0.50,
            1.00,
            0.85
        ),

        initial_inventory=
        st.sidebar.number_input(
            "Stock Inicial",
            value=100
        ),

        triage_servers=
        st.sidebar.number_input(
            "Servidores Triage",
            value=1
        ),

        crt_servers=
        st.sidebar.number_input(
            "Servidores CRT",
            value=2
        ),

        lcd_servers=
        st.sidebar.number_input(
            "Servidores LCD",
            value=1
        )
    )