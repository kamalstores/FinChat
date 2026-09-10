import { getToken, logout } from "@/lib/auth";
import { useChatSessionStore } from "@/lib/chat-store";
import { TextMessagePart, ThreadMessage } from "@assistant-ui/react";

export async function chat(message: ThreadMessage) {
     const textPart = message.content[0] as TextMessagePart;
     const token = getToken();
     const { sessionId } = useChatSessionStore.getState();

    try {
        const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/chat/generate`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    message: textPart?.text ?? "",
                    session_id: sessionId,
                }),
            }
        );
        if (response.status == 401) {
            logout();
        }
        const data = await response.json();
        return data;
    } catch (err) {
        console.error("Chat failed", err);
        return [
            {
                type: "text",
                text: "An error occurred while processing your request.",
            },
        ];
    }
}