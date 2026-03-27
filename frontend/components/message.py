import json

import plotly.graph_objects as go
import streamlit as st


def render_message(content: str) -> None:
    """Renderiza el texto de un mensaje en markdown."""
    st.markdown(content, unsafe_allow_html=False)


def render_charts(charts: list[str]) -> None:
    """Renderiza una lista de Plotly JSONs como gráficos interactivos."""
    for chart_json in charts:
        try:
            fig = go.Figure(json.loads(chart_json))
            st.plotly_chart(fig, width="stretch")
        except Exception:
            st.warning("No se pudo renderizar el gráfico.")
