"""
2.2 — Sistema de Insights Automáticos
Pipeline determinístico + LLM para redactar recomendaciones → JSON estructurado
"""
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from app.agent.select_llm import get_llm

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "Rappi_Operations_Analysis_Dummy_Data.xlsx"


def _load_df() -> pd.DataFrame:
    return pd.read_excel(_DATA_PATH)


# ---------------------------------------------------------------------------
# Análisis internos
# ---------------------------------------------------------------------------

def _detect_anomalies(df: pd.DataFrame, threshold: float = 0.10) -> pd.DataFrame:
    """Zonas con cambio WoW > threshold en la última semana."""
    tmp = df.copy()
    tmp["wow"] = (tmp["L0W_ROLL"] - tmp["L1W_ROLL"]) / tmp["L1W_ROLL"].abs()
    anomalies = tmp[tmp["wow"].abs() > threshold].copy()
    anomalies["cambio_pct"] = (anomalies["wow"] * 100).round(1)
    return (
        anomalies[["COUNTRY", "CITY", "ZONE", "METRIC", "L1W_ROLL", "L0W_ROLL", "cambio_pct"]]
        .sort_values("cambio_pct")
        .head(15)
    )


def _detect_declining_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Zonas con deterioro consistente 3+ semanas seguidas."""
    tmp = df.copy()
    tmp["declining"] = (
        (tmp["L0W_ROLL"] < tmp["L1W_ROLL"]) &
        (tmp["L1W_ROLL"] < tmp["L2W_ROLL"]) &
        (tmp["L2W_ROLL"] < tmp["L3W_ROLL"])
    )
    tmp["decline_total_pct"] = (
        (tmp["L0W_ROLL"] - tmp["L3W_ROLL"]) / tmp["L3W_ROLL"].abs() * 100
    ).round(1)
    return (
        tmp[tmp["declining"]][["COUNTRY", "CITY", "ZONE", "METRIC", "L3W_ROLL", "L0W_ROLL", "decline_total_pct"]]
        .sort_values("decline_total_pct")
        .head(15)
    )


def _benchmark_zones(df: pd.DataFrame) -> pd.DataFrame:
    """Bottom performers vs su peer group (mismo país + zone_type)."""
    df = df.copy()
    df["peer_group"] = df["COUNTRY"] + "_" + df["ZONE_TYPE"]

    peer_stats = df.groupby(["peer_group", "METRIC"])["L0W_ROLL"].agg(
        peer_mean="mean", peer_std="std"
    ).reset_index()

    df = df.merge(peer_stats, on=["peer_group", "METRIC"])
    df["z_score"] = (df["L0W_ROLL"] - df["peer_mean"]) / df["peer_std"].replace(0, np.nan)

    return (
        df[df["z_score"] < -2][["COUNTRY", "CITY", "ZONE", "ZONE_TYPE", "METRIC", "L0W_ROLL", "peer_mean", "z_score"]]
        .sort_values("z_score")
        .head(15)
        .round(3)
    )


def _find_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """Pares de métricas con correlación Spearman |r| > 0.5."""
    pivot = df.pivot_table(
        index=["COUNTRY", "CITY", "ZONE"],
        columns="METRIC",
        values="L0W_ROLL"
    )
    pivot.columns.name = None
    corr = pivot.corr(method="spearman")

    pairs = corr.unstack().reset_index()
    pairs.columns = ["metric_a", "metric_b", "correlation"]
    pairs = pairs[
        (pairs["metric_a"] < pairs["metric_b"]) &
        (pairs["correlation"].abs() > 0.5)
    ].sort_values("correlation", ascending=False).round(3)

    return pairs


# ---------------------------------------------------------------------------
# Contexto para el LLM
# ---------------------------------------------------------------------------

def _build_context(anomalies, trends, benchmarking, correlations) -> str:
    def df_to_str(df: pd.DataFrame, max_rows: int = 10) -> str:
        return df.head(max_rows).to_string(index=False)

    return f"""
=== ANOMALÍAS (cambio WoW > 10%) ===
{df_to_str(anomalies)}

=== TENDENCIAS PREOCUPANTES (deterioro 3+ semanas) ===
{df_to_str(trends)}

=== BENCHMARKING (bottom performers vs peer group, z_score < -2) ===
{df_to_str(benchmarking)}

=== CORRELACIONES ENTRE MÉTRICAS (|r| > 0.5) ===
{df_to_str(correlations)}
"""


_REPORT_PROMPT = """Eres un analista de datos senior de Rappi. Con base en los siguientes datos operacionales,
genera un reporte ejecutivo en Markdown con esta estructura exacta:

# Reporte Ejecutivo — Insights Operacionales Rappi

## Resumen Ejecutivo
Top 3-5 hallazgos críticos en bullets concisos. Cada bullet en una línea.

## 1. Anomalías Detectadas
Describe las zonas con cambios drásticos, agrupa por país si aplica. Incluye valores concretos.

## 2. Tendencias Preocupantes
Zonas en deterioro consistente 3+ semanas. Menciona magnitud del deterioro.

## 3. Benchmarking — Zonas Rezagadas
Zonas significativamente por debajo de su peer group. Explica la brecha.

## 4. Correlaciones entre Métricas
Qué métricas se mueven juntas y qué implica operacionalmente.

## 5. Oportunidades y Recomendaciones
Para cada categoría de insight, una recomendación accionable específica (no genérica).

---
Usa lenguaje ejecutivo, no técnico. Sé específico con países, zonas y métricas. Máximo 800 palabras.
Las tablas de datos del anexo se mostrarán por separado; no las incluyas aquí.

DATOS:
{context}
"""


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def generate_report() -> dict:
    """
    Ejecuta el pipeline y retorna datos estructurados para que el frontend
    construya y exporte el reporte.
    """
    df = _load_df()

    anomalies    = _detect_anomalies(df)
    trends       = _detect_declining_trends(df)
    benchmarking = _benchmark_zones(df)
    correlations = _find_correlations(df)

    context = _build_context(anomalies, trends, benchmarking, correlations)

    llm = get_llm()
    response = llm.invoke(_REPORT_PROMPT.format(context=context))

    return {
        "narrative":    response.content,
        "anomalies":    anomalies.fillna("").to_dict(orient="records"),
        "trends":       trends.fillna("").to_dict(orient="records"),
        "benchmarking": benchmarking.fillna("").to_dict(orient="records"),
        "correlations": correlations.fillna("").to_dict(orient="records"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
