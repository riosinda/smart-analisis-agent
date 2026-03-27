import httpx

API_URL = "http://localhost:8000/api/chat"
TIMEOUT = 120.0


def send_message(message: str, thread_id: str) -> str:
    """Envía un mensaje a la API y retorna el texto de respuesta."""
    response = httpx.post(
        API_URL,
        json={"message": message, "thread_id": thread_id},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["response"]
