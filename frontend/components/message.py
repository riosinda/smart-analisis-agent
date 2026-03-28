import re

import plotly.io as pio
import streamlit as st

# Gráficos se renderizan vía render_charts; eliminar cualquier imagen markdown residual
_MD_IMAGE_RE = re.compile(r'!\[.*?\]\(.*?\)')


def render_message(content: str) -> None:
    """Renderiza el texto de un mensaje en markdown."""
    clean = _MD_IMAGE_RE.sub("", content)
    st.markdown(clean, unsafe_allow_html=False)


def render_charts(charts: list[str], key_prefix: str = "") -> None:
    """Renderiza una lista de Plotly JSONs como gráficos interactivos con botón de descarga."""
    for i, chart_json in enumerate(charts):
        try:
            fig = pio.from_json(chart_json)
            st.plotly_chart(fig, width="stretch")
            html_bytes = fig.to_html(
                full_html=True, include_plotlyjs="cdn"
            ).encode("utf-8")
            st.download_button(
                label="⬇️ Descargar gráfico",
                data=html_bytes,
                file_name=f"grafico_{i + 1}.html",
                mime="text/html",
                key=f"{key_prefix}chart_dl_{i}",
            )
        except Exception as e:
            st.warning(f"No se pudo renderizar el gráfico: {e}")
