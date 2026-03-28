# Backend — Smart Analysis Agent

Servicio FastAPI que expone el agente conversacional ReAct (2.1) y el pipeline de insights automáticos (2.2).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/chat` | Consulta al agente conversacional |
| `POST` | `/api/report` | Genera reporte PDF de insights |
| `GET` | `/docs` | Swagger UI interactivo |

### POST `/api/chat`

```json
// Request
{
  "message": "¿Cuáles son las 5 zonas con mayor Lead Penetration?",
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}

// Response
{
  "response": "Las 5 zonas con mayor Lead Penetration son...",
  "charts": [{ "type": "bar", "data": { ... } }],
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

El `thread_id` identifica la sesión de conversación. Si se omite o es nuevo, se crea una sesión fresca. Reusar el mismo `thread_id` mantiene el historial de mensajes.

### POST `/api/report`

Sin body. Devuelve un PDF (`application/pdf`) con:
- Anomalías WoW (cambio > 10 %)
- Tendencias decrecientes (≥ 3 semanas consecutivas)
- Benchmark de zonas por z-score vs grupo par
- Correlaciones entre métricas (Spearman)
- Recomendaciones redactadas por el LLM

## Arquitectura interna

```
POST /api/chat
    └── LangGraph ReAct Agent (agent/graph.py)
            ├── Razona con el LLM (agent/select_llm.py)
            ├── Llama herramientas (agent/tools.py → services/)
            └── Mantiene memoria (agent/memory.py)

POST /api/report
    └── generate_insights_report() (services/report.py)
            ├── _detect_anomalies()
            ├── _detect_declining_trends()
            ├── _benchmark_zones()
            ├── _find_correlations()
            └── LLM → redactar recomendaciones (una sola llamada)
```

## Herramientas del agente

Definidas en `agent/tools.py`. Todas usan `normalize()` para matching insensible a case, tildes y espacios. El dataset tiene columnas `*_NORM` pre-computadas.

| Herramienta | Descripción |
|---|---|
| `get_top_zones` | Top/bottom N zonas por métrica con filtros opcionales |
| `compare_segments` | Compara grupos (ej. Wealthy vs Non Wealthy) en una métrica |
| `get_zone_trend` | Serie temporal para zona + métrica en N semanas |
| `aggregate_metric` | Media / mediana / suma por dimensión |
| `find_zones_multi_criteria` | Zonas que cumplen múltiples condiciones simultáneas |
| `explain_trend` | Zonas con mayor crecimiento en N semanas |
| `list_metrics` | Catálogo de métricas — útil para resolver ambigüedad |

## Configuración

Ver variables de entorno en el [README raíz](../README.md#variables-de-entorno) o en `core/config.py`.

## Ejecutar en desarrollo

```bash
# Desde la raíz del proyecto
uv run uvicorn app.main:app --reload --port 8000
```

## Ejecutar con Docker

```bash
# Desde la raíz del proyecto (build context debe ser la raíz)
docker build -f app/Dockerfile -t smart-agent-backend .
docker run -p 8000:8000 --env-file .env smart-agent-backend
```

O con Docker Compose (recomendado):

```bash
docker compose up backend
```

## Dependencias principales

| Paquete | Uso |
|---|---|
| `fastapi` | Framework web |
| `uvicorn` | Servidor ASGI |
| `langgraph` | Orquestación ReAct agent |
| `langchain-openai` / `langchain-google-genai` / `langchain-ollama` | LLM providers |
| `pandas` | Procesamiento del dataset |
| `plotly` | Generación de gráficas |
| `xhtml2pdf` | Generación de PDF |
