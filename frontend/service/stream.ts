import { getToken } from "@/lib/auth";
import { useChatSessionStore } from "@/lib/chat-store";
import { ChatModelRunResult, TextMessagePart, ThreadAssistantMessagePart, ThreadMessage } from "@assistant-ui/react";

function formatToolArgs(args: Record<string, any>) {
    return Object.entries(args)
        .map(([key, value]) => {
            if (typeof value === "object" && value !== null) {
                return `${key}: ${JSON.stringify(value)}`;
            }
            return `${key}: ${String(value)}`;
        })
        .join("\n");
}

export async function* stream(message: ThreadMessage): AsyncGenerator<ChatModelRunResult> {
    const textPart = message.content[0] as TextMessagePart;
    const token = getToken();
    const { sessionId } = useChatSessionStore.getState();
    

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/stream`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
            message: textPart?.text ?? "",
            session_id: sessionId,
        }),
    });

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    let buffer = "";
    let fullText = "";
    const contentQueue: ThreadAssistantMessagePart[] = [];

    while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
            if (!line.trim()) continue;

            const event = JSON.parse(line);

            if (event.type === "session") {
                useChatSessionStore.getState().setSessionId(event.session_id);
            }

            // text delta
            if (event.type === "text-delta") {
                fullText += event.text;

                const index = contentQueue.findIndex(
                    (part) => part.type === "text"
                );

                if (index !== -1) {
                    const existing = contentQueue[index];

                    if (existing.type === "text") {
                        contentQueue[index] = {
                            ...existing,
                            text: fullText,
                        };
                    }
                } else {
                    contentQueue.push({
                        type: "text",
                        text: fullText,
                    });
                }

                yield {
                    content: [...contentQueue],
                };
            }

            // tool call
            if (event.type === "tool-call") {
                console.log("Tool call event received in stream:", event);
                contentQueue.push({
                    type: "tool-call",
                    toolCallId: event.toolCallId,
                    toolName: event.toolName,
                    args: event.args,
                    argsText: formatToolArgs(event.args),
                });

                yield {
                    content: [...contentQueue],
                };
            }

            // tool result
            if (event.type === "tool-result") {
                console.log("Tool result event received in stream:", event);
                const index = contentQueue.findIndex(
                    (part) =>
                        part.type === "tool-call" &&
                        part.toolCallId === event.toolCallId
                );

                if (index !== -1) {
                    const existing = contentQueue[index];

                    if (existing.type === "tool-call") {
                        contentQueue[index] = {
                            ...existing,
                            result: event.result,
                        };
                    }
                }
                yield {
                    content: [...contentQueue],
                };
            }

            if (event.type === "sources") {
                console.log("Source event received in stream:", event);
                contentQueue.push({
                    type: "text",
                    text: "-----",
                });
                for (const s of event.sources) {
                    switch (s.type) {
                        case "url":
                            contentQueue.push({
                                type: "source",
                                sourceType: s.type,
                                id: `$${s.type}-${s.title}`,
                                url: s.url,
                                title: s.title,
                                mediaType: "application/pdf",
                            });
                            break;
                        case "markdown":
                            contentQueue.push({
                                type: "text",
                                text: s.content,
                            });
                            break;
                    }
                    yield {
                        content: [...contentQueue],
                    };
                }
            }
        }
    }
}
