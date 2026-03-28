import os
import uuid

import httpx
import streamlit as st

_BASE = os.environ.get("BACKEND_URL", "http://localhost:8000")
REPORT_URL = f"{_BASE}/api/report"

QUICK_QUERIES = [
    "¿Cuáles son las 5 zonas con mayor Lead Penetration esta semana?",
    "Compara Perfect Orders entre Wealthy y Non Wealthy en México",
    "¿Cuál es el promedio de Gross Profit UE por país?",
    "¿Qué zonas tienen alto Lead Penetration pero bajo Perfect Order?",
    "¿Cuáles son las zonas que más crecen en las últimas 5 semanas?",
    "Grafica la evolución de Gross Profit UE en Chapinero las últimas 8 semanas",
    "Muéstrame visualmente cómo ha ido Pro Adoption en Polanco",
]


def render_sidebar() -> str | None:
    """
    Renderiza el sidebar. Retorna una query rápida si el usuario la selecciona,
    o None si no se seleccionó ninguna.
    """
    with st.sidebar:
        st.title("Smart Analysis Agent")
        st.caption("Bot de análisis operacional · Rappi")

        st.markdown("---")

        if st.button("🔄 Nueva conversación", use_container_width=True):
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.markdown("**Reporte Automático**")

        if st.button("📊 Generar Reporte PDF", use_container_width=True):
            with st.spinner("Generando reporte..."):
                try:
                    response = httpx.post(REPORT_URL, timeout=180.0)
                    response.raise_for_status()
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=response.content,
                        file_name="reporte_insights_rappi.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except httpx.ConnectError:
                    st.error("No se pudo conectar con el servidor.")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("**Queries de ejemplo**")

        selected_query = None
        for query in QUICK_QUERIES:
            if st.button(query, use_container_width=True, key=query):
                selected_query = query

        st.markdown("---")
        st.caption(f"Thread: `{st.session_state.get('thread_id', '')[:8]}...`")

    return selected_query
