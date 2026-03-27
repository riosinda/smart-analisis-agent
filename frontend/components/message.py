import json

import plotly.graph_objects as go
import streamlit as st

CHART_PREFIX = "__CHART__:"


def render_message(content: str) -> None:
    """Renderiza un mensaje del agente: detecta gráficos o muestra markdown."""
    if content.startswith(CHART_PREFIX):
        _render_chart(content[len(CHART_PREFIX):])
    else:
        st.markdown(content, unsafe_allow_html=False)


def _render_chart(json_str: str) -> None:
    try:
        fig = go.Figure(json.loads(json_str))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.warning("No se pudo renderizar el gráfico.")
