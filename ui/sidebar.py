import streamlit as st

from simulation.config import SimulationConfig


def build_sidebar():
    """
    Construye el panel lateral de parámetros.

    Las validaciones se aplican directamente en los inputs:
    - La capacidad debe ser mayor o igual a 1.
    - El stock inicial no puede superar la capacidad.
    - No se permiten servidores menores a 1.
    - No se permiten días de simulación menores a 1.
    """

    with st.sidebar:
        st.title("⚙️ Parámetros")

        st.markdown("### Inventario")

        inventory_capacity = st.number_input(
            "Capacidad física máxima del depósito",
            min_value=1,
            value=300,
            step=10
        )

        threshold_percentage = st.slider(
            "Umbral para activar horas extra",
            min_value=0.50,
            max_value=1.00,
            value=0.85,
            step=0.01
        )

        initial_inventory_default = min(
            100,
            inventory_capacity
        )

        initial_inventory = st.number_input(
            "Stock inicial",
            min_value=0,
            max_value=inventory_capacity,
            value=initial_inventory_default,
            step=1
        )

        st.caption(
            "Los equipos que lleguen sin espacio disponible serán "
            "registrados como ingresos bloqueados."
        )

        st.divider()

        st.markdown("### Llegadas")

        arrival_lambda = st.number_input(
            "Llegadas promedio totales por día",
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
            value=15000.0,
            step=100.0
        )

        lcd_cost = st.number_input(
            "Costo procesamiento LCD",
            min_value=0.0,
            value=8000.0,
            step=100.0
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
        lcd_cost=lcd_cost
    )