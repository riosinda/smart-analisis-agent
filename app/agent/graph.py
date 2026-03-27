from langgraph.prebuilt import create_react_agent

from app.agent.memory import checkpointer
from app.agent.prompts import build_prompt
from app.agent.select_llm import get_llm


def build_agent(tools: list):
    return create_react_agent(
        model=get_llm(),
        tools=tools,
        prompt=build_prompt,
        checkpointer=checkpointer,
    )