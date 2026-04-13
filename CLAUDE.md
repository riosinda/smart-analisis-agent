# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package Manager

This project uses **uv** for dependency management.

```bash
uv sync          # Install all dependencies
uv add <pkg>     # Add a new dependency
uv run <cmd>     # Run a command in the project environment
```

## Running the Project

```bash
# Start Jupyter notebook for EDA work
uv run jupyter notebook

# Run the main application (once implemented)
uv run python -m app.main
```

## Architecture

Two deliverables share the same codebase:

- **2.1 Bot conversacional** (70%) — ReAct agent (LangGraph) that answers natural language queries about the data via tools.
- **2.2 Sistema de insights automáticos** (30%) — Standalone pipeline (`/report` endpoint) that runs deterministic analyses and uses the LLM only to draft recommendations. Not part of the agent loop.

### Directory Layout

- **`app/agent/`** — LangGraph ReAct agent (2.1)
  - `graph.py` — Agent reasoning loop
  - `prompts.py` — System prompt with business context
  - `memory.py` — Conversational memory
  - `select_llm.py` — LLM initialization
- **`app/api/`** — FastAPI layer
  - `routes.py` — `/chat` (2.1) and `/report` (2.2) endpoints
  - `schemas.py` — Pydantic request/response models
- **`app/core/config.py`** — Environment-based configuration
- **`app/services/`**
  - `tools.py` — Agent tools (2.1), validated in `notebooks/00_eda.ipynb` section 03
  - `report.py` — `generate_insights_report()` pipeline (2.2)
- **`notebooks/`** — EDA in `00_eda.ipynb`
- **`data/raw/`** — Source data (Excel files)

### Data

Primary dataset: `data/raw/Rappi_Operations_Analysis_Dummy_Data.xlsx` — 12,573 rows × 15 columns.
- **Dimensions:** COUNTRY, CITY, ZONE, ZONE_TYPE, ZONE_PRIORITIZATION, METRIC
- **Time series:** `L8W_ROLL` (8 weeks ago) → `L0W_ROLL` (current week). Nulls in older weeks = zone didn't exist yet, not missing data.
- **Metrics:** 13 operational KPIs (CVR-based 0–1 scale, Gross Profit UE different scale — normalize before cross-metric comparisons).

### Agent Tools (2.1) — defined in `app/services/tools.py`

All tools use normalized string matching. Call `normalize(text)` on inputs before filtering — handles case, accents, and whitespace. Dataset has pre-computed `*_NORM` columns (`ZONE_NORM`, `METRIC_NORM`, etc.).

| Tool | Purpose |
|---|---|
| `get_top_zones` | Top/bottom N zones by metric with optional filters |
| `compare_segments` | Compare groups (e.g. Wealthy vs Non Wealthy) on a metric |
| `get_zone_trend` | Time series for a zone+metric over N weeks |
| `aggregate_metric` | mean/median/sum by dimension (country, zone_type, etc.) |
| `find_zones_multi_criteria` | Zones matching multiple metric conditions (high A + low B) |
| `explain_trend` | Zones with highest growth over N weeks |
| `list_metrics` | Metric catalog — use to resolve ambiguous user language |

### Insights Pipeline (2.2) — `app/services/report.py`

`generate_insights_report()` runs four deterministic analyses then calls the LLM once to draft recommendations:

1. `_detect_anomalies()` — WoW change > 10%
2. `_detect_declining_trends()` — consistent decline 3+ weeks
3. `_benchmark_zones()` — z-score vs peer group (same country + zone_type)
4. `_find_correlations()` — Spearman correlation between metrics via zone pivot

Returns structured Markdown report. The LLM is not in the orchestration loop — only used for the recommendations text.

### Data Flow

```
Chat (2.1):  POST /chat  →  LangGraph ReAct Agent  →  tools.py  →  LLM response
Report (2.2): POST /report  →  report.py (deterministic)  →  LLM (redact only)  →  Markdown
```

## Environment Variables

Copy `.env.example` to `.env` and fill in values (LLM API keys, etc.) before running.

## Python Version

Python 3.12 (enforced via `.python-version`).
