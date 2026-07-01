import altair as alt
import pandas as pd
import streamlit as st
from textwrap import dedent


def inventory_chart(results, config):
    """
    Grafica el inventario fisico promedio y su tendencia visual.
    """

    days = results["DAYS"]
    storage_inventory_history = results[
        "PHYSICAL_DEPOT_AVERAGE_HISTORY"
    ]
    max_storage_inventory_history = results.get(
        "PHYSICAL_DEPOT_MAX_HISTORY",
        storage_inventory_history
    )
    trend_history = results[
        "PHYSICAL_DEPOT_TREND_HISTORY"
    ]

    min_length = min(
        len(days),
        len(storage_inventory_history),
        len(max_storage_inventory_history),
        len(trend_history)
    )

    if min_length == 0:
        st.info("No hay datos de inventario para graficar.")
        return

    capacity = config.inventory_capacity

    threshold = (
        config.inventory_capacity
        * config.threshold_percentage
    )

    days = days[:min_length]
    storage_inventory_history = (
        storage_inventory_history[:min_length]
    )
    max_storage_inventory_history = (
        max_storage_inventory_history[:min_length]
    )
    trend_history = trend_history[:min_length]

    df = _build_series_dataframe(
        days,
        {
            "Inventario fisico promedio":
                storage_inventory_history,
            "Maximo observado entre corridas":
                max_storage_inventory_history,
            "Tendencia del inventario":
                trend_history,
            "Capacidad maxima":
                [capacity] * min_length,
            "Umbral critico":
                [threshold] * min_length,
        }
    )

    max_value = max(
        capacity,
        threshold,
        max(storage_inventory_history),
        max(max_storage_inventory_history),
        max(trend_history)
    )

    chart = _line_chart(
        df,
        y_title="Equipos",
        y_domain=[
            0,
            max_value * 1.10
        ],
        color_domain=[
            "Inventario fisico promedio",
            "Maximo observado entre corridas",
            "Tendencia del inventario",
            "Capacidad maxima",
            "Umbral critico",
        ],
        color_range=[
            "#4c78a8",
            "#b279a2",
            "#54a24b",
            "#e45756",
            "#f2a900",
        ],
        dash_range=[
            [],
            [2, 2],
            [8, 4],
            [6, 4],
            [3, 3],
        ],
        show_legend=False
    )

    st.subheader("Inventario fisico del deposito")

    st.altair_chart(
        chart,
        use_container_width=True
    )

    _show_line_legend([
        {
            "label": "Inventario fisico promedio",
            "color": "#4c78a8",
            "style": "solid",
        },
        {
            "label": "Maximo observado entre corridas",
            "color": "#b279a2",
            "style": "dotted",
        },
        {
            "label": "Tendencia del inventario",
            "color": "#54a24b",
            "style": "dashed",
        },
        {
            "label": "Capacidad maxima",
            "color": "#e45756",
            "style": "dashed",
        },
        {
            "label": "Umbral critico",
            "color": "#f2a900",
            "style": "dotted",
        },
    ])

    _show_trend_caption(
        results["PHYSICAL_DEPOT_TREND_SLOPE"],
        "La linea de tendencia representa la evolucion general "
        "del inventario fisico promedio dentro del periodo simulado. "
        "El maximo observado muestra el mayor valor registrado "
        "entre corridas para cada dia."
    )


def admission_chart(results):
    """
    Grafica los equipos admitidos y bloqueados promedio por dia.
    """

    days = results["DAYS"]

    admitted_history = results["ADMITTED_HISTORY"]
    rejected_history = results["REJECTED_HISTORY"]

    min_length = min(
        len(days),
        len(admitted_history),
        len(rejected_history)
    )

    if min_length == 0:
        st.info("No hay datos de admision para graficar.")
        return

    df = pd.DataFrame({
        "Dia": days[:min_length],
        "Equipos admitidos": admitted_history[:min_length],
        "Equipos bloqueados": rejected_history[:min_length]
    })

    st.subheader("Admision diaria promedio de equipos")

    st.bar_chart(
        df,
        x="Dia",
        y=[
            "Equipos admitidos",
            "Equipos bloqueados"
        ],
        use_container_width=True
    )

    st.caption(
        "Promedios diarios entre corridas. Los equipos bloqueados "
        "representan ingresos que no pudieron entrar por falta de espacio."
    )


def processed_chart(results):
    """
    Grafica la evolucion acumulada promedio de unidades procesadas.
    """

    days = results["DAYS"]
    crt_history = results["CRT_HISTORY"]
    lcd_history = results["LCD_HISTORY"]
    irrecoverable_history = results["IRRECOVERABLE_HISTORY"]

    min_length = min(
        len(days),
        len(crt_history),
        len(lcd_history),
        len(irrecoverable_history)
    )

    if min_length == 0:
        st.info("No hay datos de procesamiento para graficar.")
        return

    df = pd.DataFrame({
        "Dia": days[:min_length],
        "CRT procesados": crt_history[:min_length],
        "LCD procesados": lcd_history[:min_length],
        "Irrecuperables procesados": irrecoverable_history[:min_length]
    })

    st.subheader("Unidades procesadas promedio acumuladas por tipo")

    st.line_chart(
        df,
        x="Dia",
        y=[
            "CRT procesados",
            "LCD procesados",
            "Irrecuperables procesados"
        ],
        use_container_width=True
    )


def cost_chart(results):
    """
    Grafica el costo acumulado promedio y su tendencia visual.
    """

    days = results["DAYS"]
    cost_history = results["COST_AVERAGE_HISTORY"]
    trend_history = results["COST_TREND_HISTORY"]

    min_length = min(
        len(days),
        len(cost_history),
        len(trend_history)
    )

    if min_length == 0:
        st.info("No hay datos de costo para graficar.")
        return

    days = days[:min_length]
    cost_history = cost_history[:min_length]
    trend_history = trend_history[:min_length]

    df = _build_series_dataframe(
        days,
        {
            "Costo acumulado promedio": cost_history,
            "Tendencia del costo": trend_history,
        }
    )

    max_value = max(
        max(cost_history),
        max(trend_history)
    )

    chart = _line_chart(
        df,
        y_title="Costo",
        y_domain=[
            0,
            max_value * 1.10
        ],
        color_domain=[
            "Costo acumulado promedio",
            "Tendencia del costo",
        ],
        color_range=[
            "#4c78a8",
            "#54a24b",
        ],
        dash_range=[
            [],
            [8, 4],
        ]
    )

    st.subheader("Evolucion promedio del costo acumulado")

    st.altair_chart(
        chart,
        use_container_width=True
    )

    _show_trend_caption(
        results["COST_TREND_SLOPE"],
        "La linea de tendencia representa la velocidad general "
        "de acumulacion de costos dentro del periodo simulado."
    )


def _build_series_dataframe(days, series_by_name):

    rows = []

    for series_name, values in series_by_name.items():
        for day, value in zip(days, values):
            rows.append({
                "Dia": day,
                "Valor": value,
                "Serie": series_name,
            })

    return pd.DataFrame(rows)


def _line_chart(
    df,
    y_title,
    y_domain,
    color_domain,
    color_range,
    dash_range,
    show_legend=True
):

    color = alt.Color(
        "Serie:N",
        title="Linea",
        scale=alt.Scale(
            domain=color_domain,
            range=color_range
        ),
        legend=alt.Legend(title="Linea") if show_legend else None
    )

    stroke_dash = alt.StrokeDash(
        "Serie:N",
        title="Linea",
        scale=alt.Scale(
            domain=color_domain,
            range=dash_range
        ),
        legend=None
    )

    return (
        alt.Chart(df)
        .mark_line(
            strokeWidth=2
        )
        .encode(
            x=alt.X(
                "Dia:Q",
                title="Dia",
                axis=alt.Axis(
                    tickMinStep=1
                )
            ),
            y=alt.Y(
                "Valor:Q",
                title=y_title,
                scale=alt.Scale(
                    domain=y_domain
                )
            ),
            color=color,
            strokeDash=stroke_dash,
            tooltip=[
                alt.Tooltip(
                    "Dia:Q",
                    title="Dia"
                ),
                alt.Tooltip(
                    "Serie:N",
                    title="Linea"
                ),
                alt.Tooltip(
                    "Valor:Q",
                    title=y_title,
                    format=",.2f"
                ),
            ]
        )
        .properties(
            height=340
        )
    )


def _show_line_legend(items):

    legend_items = []

    for item in items:

        legend_items.append(
            '<span class="chart-legend-item">'
            '<span class="chart-legend-line" '
            f'style="border-top-color: {item["color"]}; '
            f'border-top-style: {item["style"]};"></span>'
            f'<span>{item["label"]}</span>'
            '</span>'
        )

    legend_css = dedent("""
    <style>
    .chart-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        margin-top: 10px;
        margin-bottom: 14px;
    }

    .chart-legend-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        white-space: nowrap;
    }

    .chart-legend-line {
        display: inline-block;
        width: 28px;
        border-top-width: 3px;
    }
    </style>
    """).strip()

    legend_html = (
        '<div class="chart-legend">\n'
        + "\n".join(legend_items)
        + '\n</div>'
    )

    st.markdown(
        legend_css,
        unsafe_allow_html=True
    )

    st.markdown(
        legend_html,
        unsafe_allow_html=True
    )


def _show_trend_caption(slope, description):

    st.caption(
        f"{description} Pendiente estimada: {slope:.4f}. "
        "No constituye una proyeccion futura ni un criterio de aceptacion."
    )
