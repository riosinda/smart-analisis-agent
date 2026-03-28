# Frontend — Smart Analysis Agent

Interfaz web construida con Streamlit para interactuar con el agente conversacional y generar reportes.

## Pantallas

- **Chat principal** — conversación en lenguaje natural con el agente; renderiza texto, tablas y gráficas interactivas (Plotly)
- **Sidebar** — nueva conversación, queries de ejemplo, botón para generar y descargar el reporte PDF

## Estructura

```
frontend/
├── app.py              # Entry point de Streamlit; gestiona session_state
├── components/
│   ├── chat.py         # Lógica del chat y rendering de respuestas
│   ├── message.py      # Renderizado individual de mensajes (texto + gráficas)
│   └── sidebar.py      # Sidebar: nueva conversación, queries rápidas, reporte PDF
├── services/
│   └── api.py          # Cliente HTTP hacia el backend (/api/chat)
└── styles/
    └── main.css        # Estilos personalizados
```

## Ejecutar en desarrollo

```bash
# Desde la raíz del proyecto
uv run streamlit run frontend/app.py
```

La app estará disponible en http://localhost:8501.

Por defecto apunta al backend en `http://localhost:8000`. Para cambiar la URL:

```bash
BACKEND_URL=http://mi-backend:8000 uv run streamlit run frontend/app.py
```

## Ejecutar con Docker

```bash
# Desde la raíz del proyecto
docker build -f frontend/Dockerfile -t smart-agent-frontend .
docker run -p 8501:8501 -e BACKEND_URL=http://backend:8000 smart-agent-frontend
```

O con Docker Compose (recomendado):

```bash
docker compose up frontend
```

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | URL base del servicio backend |

## Session state

Streamlit mantiene el estado de la sesión en `st.session_state`:

| Clave | Tipo | Descripción |
|---|---|---|
| `thread_id` | `str` (UUID) | Identificador de la conversación activa |
| `messages` | `list[dict]` | Historial de mensajes `{role, content, charts}` |

"Nueva conversación" genera un UUID fresco y limpia el historial.

## Dependencias principales

| Paquete | Uso |
|---|---|
| `streamlit` | Framework de UI |
| `httpx` | Cliente HTTP hacia el backend |
| `plotly` | Renderizado de gráficas interactivas |
