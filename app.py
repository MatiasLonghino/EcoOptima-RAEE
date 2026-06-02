import streamlit as st

from ui.sidebar import build_sidebar
from ui.results import show_results

from simulation.simulator import Simulator

from ui.charts import (
    inventory_chart,
    processed_chart,
    cost_chart
)

st.set_page_config(
    page_title="RAEE Simulator",
    layout="wide"
)

st.title(
    "Simulador RAEE"
)

config = build_sidebar()

if st.button(
    "Ejecutar Simulación"
):

    simulator = Simulator(config)

    results = simulator.run()

    show_results(results)
    
    inventory_chart(
    results
    )

    processed_chart(
    results
    )

    cost_chart(
    results
    )
    