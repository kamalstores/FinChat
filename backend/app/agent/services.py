import json

from langchain.messages import AIMessage, HumanMessage, ToolMessage
from sqlalchemy.orm import Session

from app.agent.utils import (
    extract_sources,
    get_or_create_session,
    ndjson,
    parse_tool_content,
)
from app.model.user import User
from app.schema.chat import ChatRequest
from langgraph.graph.state import CompiledStateGraph

from app.schema.stream import StreamEventTypes, StreamEvents


def text_content(content) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                text_parts.append(block["text"])
        return "".join(text_parts)

    if isinstance(content, dict) and isinstance(content.get("text"), str):
        return content["text"]

    return ""


def run_agent(
    agent: CompiledStateGraph, request: ChatRequest, user: User, db: Session
) -> dict:
    session_id = get_or_create_session(request.session_id, user, db)
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }
    context = {"user": user, "db": db}
    msg = HumanMessage(content=request.message)
    if request.stream:
        return graph_stream(agent, {"messages": [msg]}, context=context, config=config)
    else:
        return graph_invoke(
            agent, {"messages": [msg]}, context=context, config=config
        )


def graph_invoke(agent, message, context, config) -> dict:
    response = agent.invoke(message, context=context, config=config)
    content = []
    tool_results = {}

    for msg in response["messages"]:
        if isinstance(msg, ToolMessage):
            tool_results[msg.tool_call_id] = msg.content

    for msg in response["messages"]:
        if not isinstance(msg, AIMessage):
            continue

        for tool_call in msg.tool_calls:
            content.append(
                {
                    "type": "tool-call",
                    "toolCallId": tool_call["id"],
                    "toolName": tool_call["name"],
                    "args": tool_call["args"],
                    "result": tool_results.get(tool_call["id"]),
                }
            )

        text = text_content(msg.content)
        if text:
            content.append(
                {
                    "type": "text",
                    "text": text,
                }
            )
    sources = extract_sources(response["messages"])

    return {
        "session_id": config["configurable"]["thread_id"],
        "messages": content,
        "sources": sources,
    }


async def graph_stream(agent, message, context, config):
    session_id = config["configurable"]["thread_id"]

    yield ndjson({"type": "session", "session_id": session_id})

    async for event in agent.astream_events(
        message, context=context, config=config, version="v2"
    ):
        event_type = event["event"]

        if event_type == StreamEvents.ON_MODEL_STREAM:
            chunk = event["data"]["chunk"]

            text = text_content(chunk.content)
            if text:
                yield (
                    ndjson(
                        {
                            "type": StreamEventTypes.TEXT_DELTA,
                            "text": text,
                        }
                    )
                )

        # Tool call starts
        elif event_type == StreamEvents.ON_TOOL_START:
            yield (
                ndjson(
                    {
                        "type": StreamEventTypes.TOOL_CALL,
                        "toolCallId": event["run_id"],
                        "toolName": event["name"],
                        "args": event["data"]["input"],
                        "argsText": event["data"]["input"],
                    }
                )
            )

        # Tool results
        elif event_type == StreamEvents.ON_TOOL_END:
            tool_message = event["data"]["output"]

            result = parse_tool_content(tool_message.content)
            if result is None:
                result = tool_message.content
            yield (
                ndjson(
                    {
                        "type": StreamEventTypes.TOOL_RESULT,
                        "toolCallId": event["run_id"],
                        "toolName": event["name"],
                        "args": event["data"]["input"],
                        "argsText": event["data"]["input"],
                        "result": result,
                    }
                )
            )

        elif event["event"] == StreamEvents.ON_CUSTOM_EVENT:
            if event["name"] == StreamEventTypes.SOURCES:
                yield (
                    ndjson(
                        {
                            "type": StreamEventTypes.SOURCES,
                            "sources": event["data"]["sources"],
                        }
                    )
                )
