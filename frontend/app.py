import uuid
from pathlib import Path

import streamlit as st

from components.chat import render_chat
from components.sidebar import render_sidebar

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Analysis Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
css_path = Path(__file__).parent / "styles" / "main.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
quick_query = render_sidebar()

if quick_query:
    st.session_state.quick_query = quick_query

render_chat()
