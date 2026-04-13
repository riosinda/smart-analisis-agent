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
| Frontend | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| Docs API | http://localhost:8000/docs |

### Usar Ollama (LLM local, sin API key)

```bash
# Levantar con el perfil ollama
docker compose --profile ollama up --build

# En otra terminal, descargar el modelo
docker exec -it smart-analisis-agent-ollama-1 ollama pull llama3.1
```

Asegúrate de que `.env` tenga:
```
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
```

## Desarrollo local (sin Docker)

### Prerequisitos

- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Setup

```bash
# Instalar dependencias del workspace
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu API key
```

### Ejecutar servicios

```bash
# Backend (terminal 1)
uv run uvicorn app.main:app --reload

# Frontend (terminal 2)
uv run streamlit run frontend/app.py
```

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `LLM_PROVIDER` | `openai` | Proveedor activo: `openai`, `gemini`, `ollama` |
| `OPENAI_API_KEY` | — | API key de OpenAI |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo a usar |
| `GOOGLE_API_KEY` | — | API key de Google |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Modelo Gemini |
| `OLLAMA_MODEL` | `llama3.1` | Modelo Ollama |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL del servidor Ollama |
| `TEMPERATURE` | `0.7` | Temperatura del LLM |
| `MAX_TOKENS` | `4096` | Tokens máximos por respuesta |

## Estructura del proyecto

```
smart-analisis-agent/
├── app/                    # Servicio backend (FastAPI)
│   ├── agent/              # LangGraph ReAct agent
│   ├── api/                # Endpoints y schemas
│   ├── core/               # Configuración
│   ├── services/           # Tools del agente y pipeline de reporte
│   ├── main.py
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/               # Servicio frontend (Streamlit)
│   ├── components/         # sidebar, chat, message
│   ├── services/           # Cliente HTTP al backend
│   ├── styles/             # CSS personalizado
│   ├── app.py
│   ├── pyproject.toml
│   └── Dockerfile
├── data/
│   └── raw/                # Dataset Excel (Rappi)
├── notebooks/              # EDA (00_eda.ipynb)
├── docker-compose.yml
├── .env.example
└── pyproject.toml          # Workspace uv
```

## Dataset

`data/raw/Rappi_Operations_Analysis_Dummy_Data.xlsx` — 12 573 filas × 15 columnas.

- **Dimensiones:** `COUNTRY`, `CITY`, `ZONE`, `ZONE_TYPE`, `ZONE_PRIORITIZATION`, `METRIC`
- **Serie temporal:** `L8W_ROLL` (8 semanas atrás) → `L0W_ROLL` (semana actual)
- **Métricas:** 13 KPIs operacionales (CVR en escala 0–1; `Gross Profit UE` en escala distinta — normalizar antes de comparaciones cruzadas)
- Los nulos en semanas antiguas indican que la zona no existía aún, no son datos faltantes.

## Contribuir

El proyecto usa `uv` como gestor de paquetes. No usar `pip` directamente.

```bash
uv add <paquete>          # Agregar dependencia al workspace raíz
uv add --package app <paquete>       # Agregar al backend
uv add --package frontend <paquete> # Agregar al frontend
```
