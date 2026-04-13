# Smart Analysis Agent

Bot conversacional para análisis de métricas operacionales de Rappi. Responde preguntas en lenguaje natural sobre los datos y genera reportes automáticos de insights.

## Inicio rápido con Docker

### Prerequisitos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose
- Archivo `.env` con las credenciales del LLM (ver abajo)

### 1. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tu API key
```

### 2. Levantar los servicios

```bash
docker compose up --build
```

| Servicio | URL |
|---|---|
| Chat | http://localhost:3000 |
| Reporte de insights | http://localhost:3000/report |
| Backend API | http://localhost:8000 |
| Docs API | http://localhost:8000/docs |

### Usar Ollama (LLM local, sin API key)

```bash
# Levantar con el perfil ollama
docker compose --profile ollama up --build

# En otra terminal, descargar el modelo
docker exec -it rappi-agent-ollama-1 ollama pull gemma4
```

Asegúrate de que `.env` tenga:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=gemma4
OLLAMA_BASE_URL=http://ollama:11434
```

## Desarrollo local (sin Docker)

### Prerequisitos

- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 20+

### Setup

```bash
# Instalar dependencias Python
uv sync

# Instalar dependencias del frontend
cd frontend && npm install

# Configurar variables de entorno
cp .env.example .env          # credenciales del LLM para el backend
cp frontend/.env.local.example frontend/.env.local  # URL del backend para el frontend
```

### Ejecutar servicios

```bash
# Backend (terminal 1)
uv run uvicorn app.main:app --reload

# Frontend (terminal 2)
cd frontend && npm run dev
```

## Variables de entorno

### Backend (`.env`)

| Variable | Default | Descripción |
|---|---|---|
| `LLM_PROVIDER` | `openai` | Proveedor activo: `openai`, `gemini`, `ollama` |
| `OPENAI_API_KEY` | — | API key de OpenAI |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo a usar |
| `GOOGLE_API_KEY` | — | API key de Google |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Modelo Gemini |
| `OLLAMA_MODEL` | `gemma4` | Modelo Ollama |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL del servidor Ollama |
| `TEMPERATURE` | `0.7` | Temperatura del LLM |
| `MAX_TOKENS` | `4096` | Tokens máximos por respuesta |

### Frontend (`frontend/.env.local`)

| Variable | Default | Descripción |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | URL del backend (solo server-side, no exponer) |

## Estructura del proyecto

```
smart-analisis-agent/
├── app/                        # Servicio backend (FastAPI + LangGraph)
│   ├── agent/                  # ReAct agent
│   │   ├── graph.py            # Loop de razonamiento
│   │   ├── prompts.py          # System prompt con contexto de negocio
│   │   ├── memory.py           # Memoria conversacional
│   │   └── select_llm.py      # Inicialización del LLM
│   ├── api/                    # Capa HTTP
│   │   ├── routes.py           # /chat y /report
│   │   └── schemas.py          # Modelos Pydantic
│   ├── core/config.py          # Configuración por variables de entorno
│   ├── services/
│   │   ├── tools.py            # Tools del agente
│   │   ├── explain_trend_service.py  # Lógica de crecimiento/caída
│   │   ├── zome_trend_service.py     # Lógica de tendencia por zona
│   │   └── report.py          # Pipeline de insights (2.2)
│   ├── main.py
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/                   # Servicio frontend (Next.js 15)
│   ├── app/                    # App Router de Next.js
│   │   ├── api/chat/           # BFF proxy → /api/chat del backend
│   │   ├── api/report/         # BFF proxy → /api/report del backend
│   │   └── page.tsx            # Página principal del chat
│   ├── components/
│   │   ├── MessageBubble.tsx   # Renderiza mensajes, tablas con CSV y gráficos automáticos
│   │   ├── ChartRenderer.tsx   # Gráfico Plotly con descarga PNG
│   │   └── Sidebar.tsx         # Historial de conversaciones y descarga PDF
│   ├── lib/
│   │   ├── chartUtils.ts       # Detección de tipo de gráfico y construcción de figura
│   │   └── types.ts            # Tipos compartidos (Message, Conversation)
│   ├── next.config.ts
│   ├── package.json
│   └── Dockerfile
├── data/
│   └── raw/                    # Dataset Excel (Rappi) — no versionado
├── notebooks/                  # EDA (00_eda.ipynb)
├── docker-compose.yml          # Proyecto: rappi-agent
├── .env.example
└── pyproject.toml              # Workspace uv (backend)
```

## Dataset

`data/raw/Rappi_Operations_Analysis_Dummy_Data.xlsx` — 12 573 filas × 15 columnas.

- **Dimensiones:** `COUNTRY`, `CITY`, `ZONE`, `ZONE_TYPE`, `ZONE_PRIORITIZATION`, `METRIC`
- **Serie temporal:** `L8W_ROLL` (8 semanas atrás) → `L0W_ROLL` (semana actual)
- **Métricas:** 13 KPIs operacionales (CVR en escala 0–1; `Gross Profit UE` en escala distinta — normalizar antes de comparaciones cruzadas)
- Los nulos en semanas antiguas indican que la zona no existía aún, no son datos faltantes.

## Contribuir

```bash
# Agregar dependencia al backend
uv add --package app <paquete>

# Agregar dependencia al frontend
cd frontend && npm install <paquete>
```

El proyecto usa `uv` para Python y `npm` para el frontend. No usar `pip` directamente.
