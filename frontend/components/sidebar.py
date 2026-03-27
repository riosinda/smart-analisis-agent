import uuid
import streamlit as st

QUICK_QUERIES = [
    "¿Cuáles son las 5 zonas con mayor Lead Penetration esta semana?",
    "Compara Perfect Orders entre Wealthy y Non Wealthy en México",
    "¿Cuál es el promedio de Gross Profit UE por país?",
    "¿Qué zonas tienen alto Lead Penetration pero bajo Perfect Order?",
    "¿Cuáles son las zonas que más crecen en las últimas 5 semanas?",
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
        st.markdown("**Queries de ejemplo**")

        selected_query = None
        for query in QUICK_QUERIES:
            if st.button(query, use_container_width=True, key=query):
                selected_query = query

        st.markdown("---")
        st.caption(f"Thread: `{st.session_state.get('thread_id', '')[:8]}...`")

    return selected_query
