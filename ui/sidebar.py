import streamlit as st

from simulation.config import SimulationConfig


def build_sidebar():
    """
    Construye el panel lateral de parámetros.

    Desde acá el usuario modifica los valores de entrada
    que luego se usan para crear el objeto SimulationConfig.

    Las validaciones se aplican directamente en los inputs:
    - No se permiten inventarios negativos.
    - No se permiten capacidades menores a 1.
    - No se permiten servidores menores a 1.
    - No se permiten días de simulación menores a 1.
    """

    with st.sidebar:
        st.title("⚙️ Parámetros")

        st.markdown("### Inventario")

        inventory_capacity = st.number_input(
            "Capacidad máxima del depósito",
            min_value=0,
            value=300,
            step=10
        )

        threshold_percentage = st.slider(
            "Umbral de capacidad",
            min_value=0.50,
            max_value=1.00,
            value=0.85,
            step=0.01
        )

        initial_inventory = st.number_input(
            "Stock inicial",
            min_value=0,
            max_value=inventory_capacity,
            value=100,
            step=1
        )

        st.divider()

        st.markdown("### Llegadas")

        arrival_lambda = st.number_input(
            "Llegadas promedio por día",
            min_value=0,
            value=45,
            step=1
        )

        st.divider()

        st.markdown("### Servidores")

        triage_servers = st.number_input(
            "Servidores Triage",
            min_value=1,
            value=1,
            step=1
        )

        crt_servers = st.number_input(
            "Servidores CRT",
            min_value=1,
            value=2,
            step=1
        )

        lcd_servers = st.number_input(
            "Servidores LCD",
            min_value=1,
            value=1,
            step=1
        )

        st.divider()

        st.markdown("### Tiempo de simulación")

        days = st.number_input(
            "Días simulados",
            min_value=1,
            value=30,
            step=1
        )

        workday_minutes = st.number_input(
            "Minutos jornada normal",
            min_value=1,
            value=480,
            step=30
        )

        overtime_minutes = st.number_input(
            "Minutos de horas extra",
            min_value=0,
            value=120,
            step=30
        )

        st.divider()

        st.markdown("### Costos")

        employee_daily_cost = st.number_input(
            "Costo diario por empleado",
            min_value=0.0,
            value=30.0,
            step=10.0
        )

        crt_cost = st.number_input(
            "Costo procesamiento CRT",
            min_value=0.0,
            value=1500.0,
            step=100.0
        )

        lcd_cost = st.number_input(
            "Costo procesamiento LCD",
            min_value=0.0,
            value=800.0,
            step=100.0
        )

        st.divider()

        st.markdown("### Generador propio")

        random_generator_method = st.selectbox(
            "Método de generación",
            options=[
                "lehmer",
                "mixto",
                "multiplicativo",
                "aditivo",
                "middle_square",
            ],
            index=0
        )

        random_seed = st.number_input(
            "Semilla",
            min_value=1,
            value=12345,
            step=1
        )

        lehmer_multiplier = st.number_input(
            "Multiplicador Lehmer",
            min_value=1,
            value=48271,
            step=1
        )

        generator_increment = st.number_input(
            "Incremento mixto",
            min_value=0,
            value=0,
            step=1
        )

        generator_modulus = st.number_input(
            "Módulo",
            min_value=1,
            value=2147483647,
            step=1
        )

        middle_square_seed = st.number_input(
            "Semilla cuadrado medio",
            min_value=1,
            value=1234,
            step=1
        )

        middle_square_digits = st.number_input(
            "Dígitos cuadrado medio",
            min_value=1,
            value=4,
            step=1
        )

        additive_seed_1 = st.number_input(
            "Semilla aditiva 1",
            min_value=1,
            value=1942,
            step=1
        )

        additive_seed_2 = st.number_input(
            "Semilla aditiva 2",
            min_value=1,
            value=2372,
            step=1
        )

        additive_seed_3 = st.number_input(
            "Semilla aditiva 3",
            min_value=1,
            value=5131,
            step=1
        )

        additive_seed_4 = st.number_input(
            "Semilla aditiva 4",
            min_value=1,
            value=3317,
            step=1
        )

        additive_lag_a = st.number_input(
            "Retardo aditivo A",
            min_value=1,
            value=1,
            step=1
        )

        additive_lag_b = st.number_input(
            "Retardo aditivo B",
            min_value=1,
            value=4,
            step=1
        )

        st.divider()

        st.markdown("### Prueba de los promedios")

        mean_test_sample_size = st.number_input(
            "Tamaño de muestra",
            min_value=5,
            value=30,
            step=1
        )

        mean_test_alpha = st.selectbox(
            "Nivel de significancia",
            options=[0.10, 0.05, 0.01],
            index=1
        )

    return SimulationConfig(
        days=days,
        inventory_capacity=inventory_capacity,
        threshold_percentage=threshold_percentage,
        initial_inventory=initial_inventory,
        arrival_lambda=arrival_lambda,
        triage_servers=triage_servers,
        crt_servers=crt_servers,
        lcd_servers=lcd_servers,
        workday_minutes=workday_minutes,
        overtime_minutes=overtime_minutes,
        employee_daily_cost=employee_daily_cost,
        crt_cost=crt_cost,
        lcd_cost=lcd_cost,
        generator_method=random_generator_method,
        random_seed=random_seed,
        generator_multiplier=lehmer_multiplier,
        generator_increment=generator_increment,
        generator_modulus=generator_modulus,
        middle_square_seed=middle_square_seed,
        middle_square_digits=middle_square_digits,
        additive_seed_1=additive_seed_1,
        additive_seed_2=additive_seed_2,
        additive_seed_3=additive_seed_3,
        additive_seed_4=additive_seed_4,
        additive_lag_a=additive_lag_a,
        additive_lag_b=additive_lag_b,
        mean_test_sample_size=mean_test_sample_size,
        mean_test_alpha=mean_test_alpha
    )