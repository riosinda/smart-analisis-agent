import streamlit as st
import httpx

from services.api import send_message
from components.message import render_message


def render_chat() -> None:
    """Renderiza el historial del chat y maneja el input del usuario."""

    # Historial de mensajes
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            render_message(msg["content"])

    # Input del usuario (también acepta queries rápidas del sidebar)
    prompt = st.chat_input("Preguntá sobre las métricas operacionales...")

    if st.session_state.get("quick_query"):
        prompt = st.session_state.pop("quick_query")

    if prompt:
        # Mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Llamar a la API y mostrar respuesta
        with st.chat_message("assistant"):
            with st.spinner("Analizando..."):
                try:
                    response = send_message(prompt, st.session_state.thread_id)
                except httpx.ConnectError:
                    response = "⚠️ No se pudo conectar con el servidor. ¿Está corriendo la API?"
                except httpx.HTTPStatusError as e:
                    response = f"⚠️ Error del servidor: {e.response.status_code}"

            render_message(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
