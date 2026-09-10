class StreamEvents:
    ON_MODEL_STREAM = "on_chat_model_stream"
    ON_TOOL_START = "on_tool_start"
    ON_TOOL_END = "on_tool_end"
    ON_CUSTOM_EVENT = "on_custom_event"


class StreamEventTypes:
    SESSION = "session"
    TEXT_DELTA = "text-delta"
    TOOL_CALL = "tool-call"
    TOOL_RESULT = "tool-result"
    SOURCES = "sources"