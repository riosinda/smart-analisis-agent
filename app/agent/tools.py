import unicodedata
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from langchain_core.tools import tool

from app.services.explain_trend_service import explain_trend as _explain_trend_service

# ---------------------------------------------------------------------------
# Data loading — se carga una sola vez al importar el módulo
# ---------------------------------------------------------------------------
_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "Rappi_Operations_Analysis_Dummy_Data.xlsx"

_ROLL_COLS = ["L8W_ROLL", "L7W_ROLL", "L6W_ROLL", "L5W_ROLL",
              "L4W_ROLL", "L3W_ROLL", "L2W_ROLL", "L1W_ROLL", "L0W_ROLL"]

def _load_data() -> pd.DataFrame:
    df = pd.read_excel(_DATA_PATH)
    df["ZONE_NORM"]    = df["ZONE"].apply(_normalize)
    df["CITY_NORM"]    = df["CITY"].apply(_normalize)
    df["COUNTRY_NORM"] = df["COUNTRY"].apply(_normalize)
    df["METRIC_NORM"]  = df["METRIC"].apply(_normalize)
    return df

def _normalize(text: str) -> str:
    text = str(text).lower().strip()
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

_df = _load_data()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def get_top_zones(metric: str, n: int = 5, direction: str = "desc",
                  country: str = None, zone_type: str = None) -> str:
    """
    Devuelve las N zonas con mayor o menor valor de una métrica en la semana actual (L0W_ROLL).

    Args:
        metric: Nombre de la métrica (ej: "Lead Penetration", "Gross Profit UE").
        n: Cantidad de zonas a retornar. Default 5.
        direction: "desc" para top (mayor), "asc" para bottom (menor).
        country: Código de país opcional para filtrar (ej: "MX", "BR").
        zone_type: Tipo de zona opcional ("Wealthy" o "Non Wealthy").
    """
    mask = _df["METRIC_NORM"] == _normalize(metric)
    if country:
        mask &= _df["COUNTRY_NORM"] == _normalize(country)
    if zone_type:
        mask &= _df["ZONE_TYPE"].str.lower() == zone_type.lower()

    result = (
        _df[mask][["COUNTRY", "CITY", "ZONE", "ZONE_TYPE", "ZONE_PRIORITIZATION", "L0W_ROLL"]]
        .dropna(subset=["L0W_ROLL"])
        .sort_values("L0W_ROLL", ascending=(direction == "asc"))
        .head(n)
        .reset_index(drop=True)
    )

    if result.empty:
        return f"No se encontraron zonas para la métrica '{metric}' con los filtros indicados."

    return result.to_markdown(index=False)


@tool
def compare_segments(metric: str, group_by: str, country: str = None) -> str:
    """
    Compara el valor de una métrica entre segmentos de zonas (ej: Wealthy vs Non Wealthy).

    Args:
        metric: Nombre de la métrica a comparar.
        group_by: Columna por la que agrupar. Valores válidos: "ZONE_TYPE", "ZONE_PRIORITIZATION", "COUNTRY".
        country: Código de país opcional para filtrar (ej: "MX").
    """
    mask = _df["METRIC_NORM"] == _normalize(metric)
    if country:
        mask &= _df["COUNTRY_NORM"] == _normalize(country)

    result = (
        _df[mask]
        .groupby(group_by)["L0W_ROLL"]
        .agg(
            zonas="count",
            promedio="mean",
            mediana="median",
            p25=lambda x: x.quantile(0.25),
            p75=lambda x: x.quantile(0.75),
        )
        .round(4)
    )

    if result.empty:
        return f"No se encontraron datos para la métrica '{metric}'."

    return result.to_markdown()


@tool
def get_zone_trend(zone: str, metric: str, n_weeks: int = 8) -> str:
    """
    Muestra la evolución semanal de una métrica en una zona específica.

    Args:
        zone: Nombre de la zona (puede ser parcial, ej: "Chapinero").
        metric: Nombre de la métrica.
        n_weeks: Número de semanas hacia atrás a mostrar (máximo 8). Default 8.
    """
    n_weeks = min(n_weeks, 8)
    weeks = _ROLL_COLS[-(n_weeks + 1):]

    mask = (_df["ZONE_NORM"] == _normalize(zone)) & (_df["METRIC_NORM"] == _normalize(metric))
    rows = _df[mask]

    if rows.empty:
        # intento búsqueda parcial
        mask = (_df["ZONE_NORM"].str.contains(_normalize(zone), na=False)) & \
               (_df["METRIC_NORM"] == _normalize(metric))
        rows = _df[mask]

    if rows.empty:
        return f"No se encontró la zona '{zone}' con la métrica '{metric}'."

    result = rows[["COUNTRY", "CITY", "ZONE"] + weeks].reset_index(drop=True)
    return result.round(4).to_markdown(index=False)


@tool
def aggregate_metric(metric: str, group_by: str, agg_func: str = "mean",
                     country: str = None) -> str:
    """
    Calcula un agregado (promedio, mediana, etc.) de una métrica agrupado por dimensión.

    Args:
        metric: Nombre de la métrica.
        group_by: Columna de agrupación: "COUNTRY", "ZONE_TYPE" o "ZONE_PRIORITIZATION".
        agg_func: Función de agregación: "mean", "median", "min", "max". Default "mean".
        country: Código de país opcional para filtrar.
    """
    mask = _df["METRIC_NORM"] == _normalize(metric)
    if country:
        mask &= _df["COUNTRY_NORM"] == _normalize(country)

    agg_map = {"mean": "mean", "median": "median", "min": "min", "max": "max"}
    func = agg_map.get(agg_func, "mean")

    result = (
        _df[mask]
        .groupby(group_by)["L0W_ROLL"]
        .agg(func)
        .round(4)
        .sort_values(ascending=False)
        .reset_index()
    )
    result.columns = [group_by, f"{agg_func}_{metric}"]

    if result.empty:
        return f"No se encontraron datos para la métrica '{metric}'."

    return result.to_markdown(index=False)


@tool
def find_zones_multi_criteria(criteria: list[dict]) -> str:
    """
    Encuentra zonas que cumplen múltiples condiciones sobre distintas métricas simultáneamente.
    Útil para preguntas como: "zonas con alto Lead Penetration pero bajo Perfect Order".

    Args:
        criteria: Lista de condiciones. Cada condición es un dict con:
            - metric (str): nombre de la métrica.
            - direction (str): "high" (percentil 75+) o "low" (percentil 25-).
            - threshold_pct (float, opcional): percentil personalizado (ej: 0.9). Default 0.75/0.25.

    Ejemplo:
        [{"metric": "Lead Penetration", "direction": "high"},
         {"metric": "Perfect Orders", "direction": "low"}]
    """
    pivot = _df.pivot_table(
        index=["COUNTRY", "CITY", "ZONE", "ZONE_TYPE", "ZONE_PRIORITIZATION"],
        columns="METRIC",
        values="L0W_ROLL",
    )
    pivot.columns.name = None

    base_mask = pd.Series([True] * len(pivot), index=pivot.index)
    matched_metrics = []

    for c in criteria:
        metric = c["metric"]
        direction = c["direction"]
        pct = c.get("threshold_pct", 0.75 if direction == "high" else 0.25)

        col = next((col for col in pivot.columns if _normalize(col) == _normalize(metric)), None)
        if col is None:
            return f"Métrica '{metric}' no encontrada. Usá list_metrics para ver las disponibles."

        threshold = pivot[col].quantile(pct)
        base_mask &= pivot[col] >= threshold if direction == "high" else pivot[col] <= threshold
        matched_metrics.append(col)

    result = pivot[base_mask][matched_metrics].reset_index()

    if result.empty:
        return "No se encontraron zonas que cumplan todos los criterios simultáneamente."

    return result.round(4).to_markdown(index=False)


@tool
def explain_trend(n_weeks: int = 5, top_n: int = 10, direction: str = "top",
                  country: str = None, metric: str = None,
                  zone_type: str = None) -> str:
    """
    Identifica las zonas con mayor crecimiento o mayor caída en las últimas N semanas.
    Útil para preguntas como "¿qué zonas están creciendo más?" o "¿qué zonas están cayendo?".

    Args:
        n_weeks: Ventana de semanas para medir la variación (máximo 8). Default 5.
        top_n: Cantidad de zonas a retornar. Default 10.
        direction: "top" para zonas que más crecieron, "bottom" para zonas que más cayeron.
        country: Filtrar por código de país (ej: "MX", "CO"). Default None (todos los países).
        metric: Filtrar por métrica específica. Default None (todas las métricas).
        zone_type: Filtrar por tipo de zona ("Wealthy" o "Non Wealthy"). Default None.
    """
    result = _explain_trend_service(
        _df,
        n_weeks=n_weeks,
        top_n=top_n,
        direction=direction,
        country=country,
        metric=metric,
        zone_type=zone_type,
    )

    if result.empty:
        return "No se encontraron datos con los filtros indicados."

    return result.to_markdown(index=False)


@tool
def list_metrics() -> str:
    """
    Lista todas las métricas disponibles en el dataset con su descripción.
    Usar cuando el usuario menciona términos ambiguos como "conversión" o "ganancias"
    para identificar la métrica exacta antes de llamar otra tool.
    """
    descriptions = {
        "% PRO Users Who Breakeven": "Usuarios Pro cuyo valor generado cubre el costo de membresía / Total usuarios Pro",
        "% Restaurants Sessions With Optimal Assortment": "Sesiones con mínimo 40 restaurantes / Total sesiones",
        "Gross Profit UE": "Margen bruto de ganancia / Total de órdenes",
        "Lead Penetration": "Tiendas habilitadas / (leads + habilitadas + salidas de Rappi)",
        "MLTV Top Verticals Adoption": "Usuarios con órdenes en diferentes verticales / Total usuarios",
        "Non-Pro PTC > OP": "Conversión No Pro de 'Proceed to Checkout' a 'Order Placed'",
        "Perfect Orders": "Órdenes sin cancelaciones, defectos o demora / Total órdenes",
        "Pro Adoption": "Usuarios suscripción Pro / Total usuarios Rappi",
        "Restaurants Markdowns / GMV": "Descuentos totales en restaurantes / GMV Restaurantes",
        "Restaurants SS > ATC CVR": "Conversión en restaurantes de 'Select Store' a 'Add to Cart'",
        "Restaurants SST > SS CVR": "Usuarios que seleccionan un restaurante de la lista presentada",
        "Retail SST > SS CVR": "Usuarios que seleccionan un supermercado de la lista presentada",
        "Turbo Adoption": "Usuarios comprando en Turbo / Usuarios con tiendas turbo disponible",
    }
    available = sorted(_df["METRIC"].unique())
    lines = [f"- **{m}**: {descriptions.get(m, 'Sin descripción')}" for m in available]
    return "\n".join(lines)


CHART_PREFIX = "__CHART__:"


@tool
def plot_zone_trend(zone: str, metric: str, n_weeks: int = 8) -> str:
    """
    Genera un gráfico interactivo de la evolución semanal de una métrica en una zona.
    Usar cuando el usuario pida "grafica", "muéstrame visualmente", "ver la evolución" o "cómo ha ido".
    Para obtener los datos en tabla usar get_zone_trend en su lugar.

    Args:
        zone: Nombre de la zona (puede ser parcial, ej: "Chapinero").
        metric: Nombre de la métrica.
        n_weeks: Semanas hacia atrás a graficar (máximo 8). Default 8.
    """
    n_weeks = min(n_weeks, 8)
    weeks = _ROLL_COLS[-(n_weeks + 1):]
    week_labels = [f"L{8 - i}W" for i in range(len(weeks))]

    mask = (_df["ZONE_NORM"] == _normalize(zone)) & (_df["METRIC_NORM"] == _normalize(metric))
    rows = _df[mask]

    if rows.empty:
        mask = (_df["ZONE_NORM"].str.contains(_normalize(zone), na=False)) & \
               (_df["METRIC_NORM"] == _normalize(metric))
        rows = _df[mask]

    if rows.empty:
        return f"No se encontró la zona '{zone}' con la métrica '{metric}'."

    fig = go.Figure()

    for _, row in rows.iterrows():
        values = [row[w] for w in weeks]
        fig.add_trace(go.Scatter(
            x=week_labels,
            y=values,
            mode="lines+markers",
            name=f"{row['ZONE']} ({row['COUNTRY']})",
            line=dict(width=2),
            marker=dict(size=7),
        ))

    fig.update_layout(
        title=f"{metric} — {zone}",
        xaxis_title="Semana",
        yaxis_title="Valor",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
    )

    return CHART_PREFIX + fig.to_json()


# Lista de tools para registrar en el agente
TOOLS = [
    get_top_zones,
    compare_segments,
    get_zone_trend,
    plot_zone_trend,
    aggregate_metric,
    find_zones_multi_criteria,
    explain_trend,
    list_metrics,
]
