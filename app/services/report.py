"""
2.2 — Sistema de Insights Automáticos
Pipeline determinístico + LLM para redactar recomendaciones → PDF
"""
from pathlib import Path

import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import markdown
import numpy as np
import pandas as pd
from xhtml2pdf import pisa

from app.agent.select_llm import get_llm

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "Rappi_Operations_Analysis_Dummy_Data.xlsx"
_ROLL_COLS = ["L8W_ROLL", "L7W_ROLL", "L6W_ROLL", "L5W_ROLL",
              "L4W_ROLL", "L3W_ROLL", "L2W_ROLL", "L1W_ROLL", "L0W_ROLL"]


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
# Formateo del contexto para el LLM
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


# ---------------------------------------------------------------------------
# Anexo: tablas HTML + gráficos matplotlib
# ---------------------------------------------------------------------------

def _fig_to_b64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return b64


def _df_to_html(df: pd.DataFrame) -> str:
    return df.to_html(index=False, border=0, classes="data-table")


def _build_appendix_html(
    anomalies: pd.DataFrame,
    trends: pd.DataFrame,
    benchmarking: pd.DataFrame,
    correlations: pd.DataFrame,
) -> str:
    sections = []

    # --- Gráfico: Top Anomalías ---
    if not anomalies.empty:
        top = anomalies.head(10).copy()
        top["label"] = top["ZONE"].str[:18] + " · " + top["METRIC"].str[:14]
        colors = ["#e74c3c" if v < 0 else "#27ae60" for v in top["cambio_pct"]]

        fig, ax = plt.subplots(figsize=(9, max(3, len(top) * 0.45)))
        ax.barh(top["label"], top["cambio_pct"], color=colors)
        ax.axvline(0, color="#333", linewidth=0.6)
        ax.set_title("Top Anomalías WoW (%)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Cambio %")
        ax.tick_params(labelsize=8)
        fig.tight_layout()

        b64 = _fig_to_b64(fig)
        sections.append(
            f"<h3>Gráfico: Anomalías WoW</h3>"
            f'<img src="data:image/png;base64,{b64}" style="width:100%;margin-bottom:8px;">'
        )

    # --- Gráfico: Tendencias Decrecientes ---
    if not trends.empty:
        top = trends.head(10).copy()
        top["label"] = top["ZONE"].str[:18] + " · " + top["METRIC"].str[:14]

        fig, ax = plt.subplots(figsize=(9, max(3, len(top) * 0.45)))
        ax.barh(top["label"], top["decline_total_pct"], color="#e67e22")
        ax.axvline(0, color="#333", linewidth=0.6)
        ax.set_title("Top Tendencias Decrecientes — 3 semanas (%)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Deterioro %")
        ax.tick_params(labelsize=8)
        fig.tight_layout()

        b64 = _fig_to_b64(fig)
        sections.append(
            f"<h3>Gráfico: Tendencias Decrecientes</h3>"
            f'<img src="data:image/png;base64,{b64}" style="width:100%;margin-bottom:8px;">'
        )

    # --- Tablas de datos ---
    tables = [
        ("Tabla: Anomalías WoW", anomalies),
        ("Tabla: Tendencias Decrecientes", trends),
        ("Tabla: Benchmarking — Zonas Rezagadas", benchmarking),
        ("Tabla: Correlaciones entre Métricas", correlations),
    ]
    for title, df in tables:
        if not df.empty:
            sections.append(f"<h3>{title}</h3>{_df_to_html(df)}")

    if not sections:
        return ""

    return (
        '<hr><h2 style="color:#1e3a5f;">Anexo — Datos del Análisis</h2>'
        + "".join(sections)
    )


# ---------------------------------------------------------------------------
# Generación del reporte
# ---------------------------------------------------------------------------

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
Las tablas y gráficos de datos se agregarán automáticamente al final del reporte; no las incluyas aquí.

DATOS:
{context}
"""


def generate_report() -> bytes:
    """
    Ejecuta el pipeline completo y retorna el PDF como bytes.
    """
    df = _load_df()

    anomalies    = _detect_anomalies(df)
    trends       = _detect_declining_trends(df)
    benchmarking = _benchmark_zones(df)
    correlations = _find_correlations(df)

    context = _build_context(anomalies, trends, benchmarking, correlations)

    llm = get_llm()
    response = llm.invoke(_REPORT_PROMPT.format(context=context))
    report_markdown = response.content

    appendix_html = _build_appendix_html(anomalies, trends, benchmarking, correlations)

    return _to_pdf(report_markdown, appendix_html)


def _to_pdf(md_text: str, appendix_html: str = "") -> bytes:
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 13px;
          line-height: 1.6; color: #1a1a1a; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
  h1 {{ color: #ff4b00; border-bottom: 2px solid #ff4b00; padding-bottom: 8px; }}
  h2 {{ color: #1e3a5f; margin-top: 28px; border-left: 4px solid #ff4b00; padding-left: 10px; }}
  h3 {{ color: #1e3a5f; margin-top: 20px; }}
  table, .data-table {{ border-collapse: collapse; width: 100%; font-size: 10px; margin: 12px 0; }}
  th {{ background: #1e3a5f; color: white; padding: 5px 8px; text-align: left; }}
  td {{ padding: 4px 8px; border-bottom: 1px solid #ddd; }}
  tr:nth-child(even) td {{ background: #f7f9fc; }}
  ul {{ padding-left: 20px; }} li {{ margin-bottom: 4px; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 24px 0; }}
  code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-size: 11px; }}
  img {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>{html_body}{appendix_html}</body>
</html>"""

    buffer = io.BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    return buffer.getvalue()
