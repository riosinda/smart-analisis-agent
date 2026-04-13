from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, ToolMessage

from app.agent.graph import build_agent
from app.agent.tools import TOOLS, CHART_PREFIX
from app.api.schemas import ChatRequest, ChatResponse, ReportResponse
from app.services.report import generate_report

router = APIRouter()

_agent = build_agent(TOOLS)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Endpoint conversacional del bot (2.1).
    El thread_id mantiene la memoria entre mensajes del mismo usuario.
    """
    config = {"configurable": {"thread_id": request.thread_id}}

    try:
        result = await _agent.ainvoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    messages = result["messages"]
    response_text = messages[-1].content

    # Extraer solo los ToolMessages de esta invocación (después del último HumanMessage)
    last_human_idx = max(
        i for i, m in enumerate(messages) if isinstance(m, HumanMessage)
    )
    charts = [
        msg.content[len(CHART_PREFIX):]
        for msg in messages[last_human_idx:]
        if isinstance(msg, ToolMessage) and msg.content.startswith(CHART_PREFIX)
    ]

    return ChatResponse(response=response_text, charts=charts, thread_id=request.thread_id)


@router.post("/report", response_model=ReportResponse)
async def report() -> ReportResponse:
    """
    Genera el reporte ejecutivo de insights automáticos (2.2).
    Retorna JSON estructurado: narrativa LLM + 4 tablas de datos para
    que el frontend construya y exporte el reporte.
    """
    try:
        data = generate_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ReportResponse(**data)