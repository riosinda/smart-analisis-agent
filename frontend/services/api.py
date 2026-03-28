import os

import httpx

_BASE = os.environ.get("BACKEND_URL", "http://localhost:8000")
API_URL = f"{_BASE}/api/chat"
TIMEOUT = 120.0


def send_message(message: str, thread_id: str) -> dict:
    """Envía un mensaje a la API y retorna {response, charts, thread_id}."""
    response = httpx.post(
        API_URL,
        json={"message": message, "thread_id": thread_id},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()
