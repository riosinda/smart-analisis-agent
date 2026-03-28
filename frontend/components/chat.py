import streamlit as st
import httpx

from services.api import send_message
from components.message import render_message, render_charts


def render_chat() -> None:
    """Renderiza el historial del chat y maneja el input del usuario."""

    # Historial de mensajes
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            render_message(msg["content"])
            if msg.get("charts"):
                render_charts(msg["charts"], key_prefix=f"hist_{idx}_")

    # Input del usuario (también acepta queries rápidas del sidebar)
    prompt = st.chat_input("Preguntá sobre las métricas operacionales...")

    if st.session_state.get("quick_query"):
        prompt = st.session_state.pop("quick_query")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analizando..."):
                try:
                    result = send_message(prompt, st.session_state.thread_id)
                    response = result["response"]
                    charts = result.get("charts", [])
                except httpx.ConnectError:
                    response = "⚠️ No se pudo conectar con el servidor. ¿Está corriendo la API?"
                    charts = []
                except httpx.HTTPStatusError as e:
                    response = f"⚠️ Error del servidor: {e.response.status_code}"
                    charts = []

            render_message(response)
            render_charts(charts, key_prefix="new_")

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "charts": charts,
        })
