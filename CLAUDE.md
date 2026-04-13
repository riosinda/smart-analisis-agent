# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package Manager

Python backend uses **uv**. Frontend uses **npm**.

```bash
# Backend
uv sync                            # Install all Python dependencies
uv add --package app <pkg>         # Add backend dependency
uv run <cmd>                       # Run command in project environment

# Frontend
cd frontend && npm install         # Install Node dependencies
cd frontend && npm run dev         # Start dev server (port 3000)
cd frontend && npm run build       # Production build
```

## Running the Project

```bash
# Backend (terminal 1)
uv run uvicorn app.main:app --reload     # port 8000

# Frontend (terminal 2)
cd frontend && npm run dev               # port 3000

# Or with Docker (project name: rappi-agent)
docker compose up --build
```

## Architecture

Two deliverables share the same codebase:

- **2.1 Bot conversacional** (70%) — ReAct agent (LangGraph) that answers natural language queries about the data via tools.
- **2.2 Sistema de insights automáticos** (30%) — Standalone pipeline (`/report` endpoint) that runs deterministic analyses and uses the LLM only to draft recommendations. Not part of the agent loop.

### Directory Layout

**Backend (`app/`)**
- **`app/agent/`** — LangGraph ReAct agent (2.1)
  - `graph.py` — Agent reasoning loop
  - `prompts.py` — System prompt with business context and few-shot examples
  - `memory.py` — Conversational memory
  - `select_llm.py` — LLM initialization (openai / gemini / ollama)
- **`app/api/`** — FastAPI layer (router registered with `prefix="/api"`)
  - `routes.py` — `POST /api/chat` (2.1) and `POST /api/report` (2.2)
  - `schemas.py` — Pydantic request/response models
- **`app/core/config.py`** — Environment-based configuration
- **`app/services/`**
  - `tools.py` — Agent tools, registered in `TOOLS` list
  - `explain_trend_service.py` — Pure function for growth/decline analysis (called by `explain_trend` tool)
  - `zome_trend_service.py` — Zone trend service
  - `report.py` — `generate_insights_report()` pipeline (2.2)

**Frontend (`frontend/`)**
- Next.js 15 App Router, TypeScript, Tailwind CSS
- **`app/api/chat/route.ts`** — BFF proxy: `POST /api/chat` → `${BACKEND_URL}/api/chat`
- **`app/api/report/route.ts`** — BFF proxy: `POST /api/report` → `${BACKEND_URL}/api/report`
- **`components/MessageBubble.tsx`** — Renders messages; overrides `<table>` to add CSV download button and auto-generate charts from table data
- **`components/ChartRenderer.tsx`** — Plotly chart with PNG download via SVG→canvas
- **`components/Sidebar.tsx`** — Conversation history (localStorage) and PDF export
- **`lib/chartUtils.ts`** — `detectChartType()` and `buildFigure()` for auto-chart logic
- **`lib/types.ts`** — Shared types: `Message`, `Conversation`

### Data

Primary dataset: `data/raw/Rappi_Operations_Analysis_Dummy_Data.xlsx` — 12,573 rows × 15 columns.
- **Dimensions:** COUNTRY, CITY, ZONE, ZONE_TYPE, ZONE_PRIORITIZATION, METRIC
- **Time series:** `L8W_ROLL` (8 weeks ago) → `L0W_ROLL` (current week). Nulls in older weeks = zone didn't exist yet, not missing data.
- **Metrics:** 13 operational KPIs (CVR-based 0–1 scale, Gross Profit UE different scale — normalize before cross-metric comparisons).

### Agent Tools (2.1) — defined in `app/services/tools.py`

All tools use normalized string matching. Call `_normalize(text)` on inputs before filtering — handles case, accents, and whitespace. Dataset has pre-computed `*_NORM` columns (`ZONE_NORM`, `METRIC_NORM`, etc.).

| Tool | Purpose |
|---|---|
| `get_top_zones` | Top/bottom N zones by metric with optional filters |
| `compare_segments` | Compare groups (e.g. Wealthy vs Non Wealthy) on a metric |
| `get_zone_trend` | Time series table for a zone+metric over N weeks |
| `plot_zone_trend` | Interactive Plotly chart for a zone+metric (use when user asks for a visual) |
| `aggregate_metric` | mean/median/sum by dimension (country, zone_type, etc.) |
| `find_zones_multi_criteria` | Zones matching multiple metric conditions (high A + low B) |
| `explain_trend` | Zones with highest growth or steepest decline over N weeks |
| `list_metrics` | Metric catalog — use to resolve ambiguous user language |

**`explain_trend` params:**
- `direction`: `"top"` (growing) or `"bottom"` (declining)
- `zone_type`: `"Wealthy"` / `"Non Wealthy"` / `None`
- `zone_prioritization`: `"High Priority"` etc. / `None`
- Returns columns: `COUNTRY, CITY, ZONE, METRIC, <start_col>, L0W_ROLL, growth_abs, growth_pct`

**`plot_zone_trend`** returns a JSON string prefixed with `__CHART__:`. The frontend strips the prefix and passes the JSON to `ChartRenderer`.

### Auto-chart logic — `frontend/lib/chartUtils.ts`

`detectChartType(data)` decides whether to auto-generate a chart from a markdown table:
- **line**: every first-column cell contains `L\d+W` (matches both `"L8W"` and `"8 semanas atrás (L8W)"`)
- **bar**: exactly 2 columns (1 category + 1 numeric value)
- **null** (no chart): 3+ columns, or no numeric values — suppresses chart for multi-dimensional analytical tables

`buildFigure()` normalizes week labels to `LxW` format on the x-axis.

### Insights Pipeline (2.2) — `app/services/report.py`

`generate_report()` runs four deterministic analyses then calls the LLM once to draft the narrative:

1. `_detect_anomalies()` — WoW change > 10%
2. `_detect_declining_trends()` — consistent decline 3+ weeks
3. `_benchmark_zones()` — z-score vs peer group (same country + zone_type)
4. `_find_correlations()` — Spearman correlation between metrics via zone pivot

Returns a **structured JSON dict** (not PDF): `narrative` (LLM markdown) + 4 lists of records (`anomalies`, `trends`, `benchmarking`, `correlations`) + `generated_at`. The LLM is used only for the narrative text.

The report UI lives at `frontend/app/report/page.tsx`:
- Renders the LLM narrative as styled markdown
- Renders a Plotly horizontal bar chart + data table for each of the 4 sections
- "Imprimir / PDF" button uses `window.print()` with `@page` A4 landscape CSS
- Navigated to from the sidebar ("Ver Reporte de Insights" button)

### Data Flow

```
Chat (2.1):
  POST /api/chat  →  Next.js BFF  →  FastAPI /api/chat  →  LangGraph ReAct  →  tools.py  →  LLM

Report (2.2):
  POST /api/report  →  Next.js BFF  →  FastAPI /api/report  →  report.py (deterministic)  →  LLM (text only)  →  Markdown
```

## Environment Variables

**Backend** — copy `.env.example` to `.env`:
- `LLM_PROVIDER`: `openai` | `gemini` | `ollama`
- `OPENAI_API_KEY`, `GOOGLE_API_KEY` — LLM credentials
- `OLLAMA_MODEL`: default `gemma4:e4b`

**Frontend** — copy `frontend/.env.local.example` to `frontend/.env.local`:
- `BACKEND_URL` — server-side only (no `NEXT_PUBLIC_` prefix), used in BFF API routes

In Docker, `BACKEND_URL=http://backend:8000` is set via `docker-compose.yml` (service DNS).

## Python Version

Python 3.12 (enforced via `.python-version`).

## Node Version

Node.js 20+ (frontend). Docker image: `node:20-alpine`.
