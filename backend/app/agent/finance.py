from typing_extensions import TypedDict
from langchain_core.callbacks.manager import adispatch_custom_event

from langgraph.graph import END, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.provider.gemini import model
from sqlalchemy.orm import Session

from app.agent.prompts import system_prompt
from app.agent.tools import rag_search, sql_query
from app.agent.utils import extract_sources
from app.model.user import User

class Context(TypedDict):
    user: User
    db: Session

tools = [sql_query, rag_search]


def generate(state: MessagesState) -> dict:
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    response = model.bind_tools(tools).invoke(messages)
    return {"messages": [response]}


async def return_sources(state: MessagesState):
    await adispatch_custom_event(
        "sources",
        {"sources": extract_sources(state["messages"])},
    )


def create_finance_agent(checkpointer) -> CompiledStateGraph:
    workflow = StateGraph(MessagesState, Context)

    workflow.add_node("generate", generate)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("return_sources", return_sources)

    workflow.set_entry_point("generate")
    workflow.add_conditional_edges(
        "generate", tools_condition, {"tools": "tools", END: "return_sources"}
    )
    workflow.add_edge("tools", "generate")
    workflow.set_finish_point("return_sources")

    return workflow.compile(checkpointer=checkpointer)
