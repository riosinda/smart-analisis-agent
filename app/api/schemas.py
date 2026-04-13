from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensaje del usuario")
    thread_id: str = Field(..., description="ID de conversación para mantener memoria entre mensajes")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Respuesta del agente")
    charts: list[str] = Field(default_factory=list, description="Plotly JSONs de gráficos generados")
    thread_id: str = Field(..., description="ID de conversación")


class ReportResponse(BaseModel):
    narrative: str = Field(..., description="Narrativa ejecutiva en Markdown generada por el LLM")
    anomalies: list[dict] = Field(default_factory=list, description="Cambios WoW > 10%")
    trends: list[dict] = Field(default_factory=list, description="Deterioro consistente 3+ semanas")
    benchmarking: list[dict] = Field(default_factory=list, description="Zonas rezagadas vs peer group")
    correlations: list[dict] = Field(default_factory=list, description="Pares de métricas correlacionadas")
    generated_at: str = Field(..., description="Timestamp ISO de generación")
