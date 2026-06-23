import streamlit as st

from ui.sidebar import build_sidebar
from ui.results import show_results
from ui.styles import apply_custom_styles

from simulation.simulator import Simulator

from ui.charts import (
    inventory_chart,
    admission_chart,
    processed_chart,
    cost_chart
)


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
    considerando capacidad física del depósito, ingresos bloqueados,
    clasificación, procesamiento y costos acumulados.
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

    try:
        simulator = Simulator(config)

        results = simulator.run()

        st.divider()

        show_results(results)

        st.divider()

        # Ahora recibe config para dibujar capacidad y umbral.
        inventory_chart(results, config)

        st.divider()

        # Muestra admitidos y bloqueados por falta de capacidad.
        admission_chart(results)

        st.divider()

        processed_chart(results)

        st.divider()

        cost_chart(results)

    except ValueError as error:
        st.error(f"Error de configuración: {error}")

    except RuntimeError as error:
        st.error(f"Error durante la simulación: {error}")

else:
    st.info(
        "Configurá los parámetros desde el panel lateral y ejecutá la simulación."
    )