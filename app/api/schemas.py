from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensaje del usuario")
    thread_id: str = Field(..., description="ID de conversación para mantener memoria entre mensajes")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Respuesta del agente")
    charts: list[str] = Field(default_factory=list, description="Plotly JSONs de gráficos generados")
    thread_id: str = Field(..., description="ID de conversación")
