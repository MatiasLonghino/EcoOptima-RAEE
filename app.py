import streamlit as st

from ui.sidebar import build_sidebar
from ui.results import show_results
from ui.styles import apply_custom_styles

from simulation.simulator import Simulator

import ui.charts as charts
import os
st.write("APP ejecutado desde:")
st.code(os.path.abspath(__file__))

st.write("CHARTS cargado desde:")
st.code(charts.__file__)
st.set_page_config(
    page_title="RAEE Simulator",
    page_icon="♻️",
    layout="wide"
)


apply_custom_styles()


st.title("♻️ Simulador RAEE")

st.markdown(
    """
    <p class="app-caption">
    Simulación del procesamiento de monitores y pantallas RAEE,
    considerando inventario, capacidad operativa, clasificación,
    procesamiento y costos acumulados.
    </p>
    """,
    unsafe_allow_html=True
)


config = build_sidebar()


run_button = st.button(
    "▶ Ejecutar simulación",
    type="primary"
)


if run_button:

    simulator = Simulator(config)

    results = simulator.run()

    st.divider()

    show_results(results)

    st.divider()

    charts.inventory_chart(
        results
    )

    st.divider()

    charts.processed_chart(
        results
    )

    st.divider()

    charts.cost_chart(
        results
    )

else:
    st.info(
        "Configurá los parámetros desde el panel lateral y ejecutá la simulación."
    )