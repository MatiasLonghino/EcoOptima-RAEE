from types import SimpleNamespace

import streamlit as st

from ui.sidebar import build_sidebar
from ui.results import show_results
from ui.styles import apply_custom_styles

from simulation.exporters import (
    build_export_dataframes,
    dataframe_to_csv_bytes
)
from simulation.simulator import Simulator

from ui.charts import (
    inventory_chart,
    admission_chart,
    processed_chart,
    cost_chart
)


def show_download_buttons(scenario_id, export_dataframes):

    if export_dataframes is None:
        return

    st.subheader("Exportacion CSV")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="Descargar detalle por corrida",
            data=dataframe_to_csv_bytes(
                export_dataframes["runs"]
            ),
            file_name=f"corridas_{scenario_id}.csv",
            mime="text/csv",
            key=f"download_runs_{scenario_id}"
        )

    with col2:
        st.download_button(
            label="Descargar historial diario",
            data=dataframe_to_csv_bytes(
                export_dataframes["daily_history"]
            ),
            file_name=f"historial_diario_{scenario_id}.csv",
            mime="text/csv",
            key=f"download_daily_{scenario_id}"
        )

    with col3:
        st.download_button(
            label="Descargar resumen agregado",
            data=dataframe_to_csv_bytes(
                export_dataframes["summary"]
            ),
            file_name=f"resumen_{scenario_id}.csv",
            mime="text/csv",
            key=f"download_summary_{scenario_id}"
        )


st.set_page_config(
    page_title="RAEE Simulator",
    page_icon=":recycle:",
    layout="wide"
)


apply_custom_styles()


st.title("Simulador RAEE")

st.markdown(
    """
    <p class="app-caption">
    Simulacion del procesamiento de monitores y pantallas RAEE,
    considerando capacidad fisica del deposito, ingresos bloqueados,
    clasificacion, procesamiento y costos acumulados.
    </p>
    """,
    unsafe_allow_html=True
)


config = build_sidebar()


if "latest_experiment_results" not in st.session_state:
    st.session_state.latest_experiment_results = None

if "latest_export_dataframes" not in st.session_state:
    st.session_state.latest_export_dataframes = None


run_button = st.button(
    "Ejecutar simulacion",
    type="primary"
)


if run_button:

    try:
        simulator = Simulator(config)

        results = simulator.run_multiple()

        export_dataframes = build_export_dataframes(
            results
        )

        st.session_state.latest_experiment_results = results
        st.session_state.latest_export_dataframes = export_dataframes

    except ValueError as error:
        st.error(f"Error de configuracion: {error}")
        st.stop()

    except RuntimeError as error:
        st.error(f"Error durante la simulacion: {error}")
        st.stop()


results = st.session_state.latest_experiment_results
export_dataframes = st.session_state.latest_export_dataframes


if results is not None:

    aggregated_results = results["AGGREGATED_RESULTS"]
    scenario_id = results["SCENARIO_ID"]
    scenario_config = SimpleNamespace(
        **results["CONFIG"]
    )

    st.caption(
        f"Escenario vigente: {scenario_id}. "
        "Las descargas usan estos resultados ya calculados."
    )

    st.divider()

    show_results(results)

    st.divider()

    show_download_buttons(
        scenario_id,
        export_dataframes
    )

    st.divider()

    inventory_chart(aggregated_results, scenario_config)

    st.divider()

    admission_chart(aggregated_results)

    st.divider()

    processed_chart(aggregated_results)

    st.divider()

    cost_chart(aggregated_results)

else:
    st.info(
        "Configura los parametros desde el panel lateral y ejecuta la simulacion."
    )
