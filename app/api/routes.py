from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

from app.agent.graph import build_agent
from app.agent.tools import TOOLS
from app.api.schemas import ChatRequest, ChatResponse

router = APIRouter()

# El agente se instancia una sola vez al arrancar la app
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
        response_text = result["messages"][-1].content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(response=response_text, thread_id=request.thread_id)
