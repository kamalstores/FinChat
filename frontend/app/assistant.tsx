"use client";

import { AssistantRuntimeProvider, ChatModelAdapter, useLocalRuntime } from "@assistant-ui/react";
import { toast } from "sonner"
import { Thread } from "@/components/assistant-ui/thread";
import { chat } from "@/service/chat";
import { logout } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { stream } from "@/service/stream";
import { useAuthStore } from "@/lib/profile-store";
import { useEffect } from "react";
import { useChatSessionStore } from "@/lib/chat-store";

const _InvokeRuntime: ChatModelAdapter = {
  async run({
    messages,
  }) {
    const lastMessage = messages[messages.length - 1];
    const message = await chat(lastMessage);

    return { 'content': message };
  },
};

const StreamRuntime: ChatModelAdapter = {
  async *run({
    messages,
  }) {
    const lastMessage = messages[messages.length - 1];

    for await (const message of stream(lastMessage)) {
      yield message;
    }
  },
};

export const Assistant = () => {
  const router = useRouter();
  const runtime = useLocalRuntime(StreamRuntime);
  const loadProfile = useAuthStore((s) => s.loadProfile);

  function handleLogout() {
    logout();
    toast("Logged out.");
    router.replace("/login");
  }

  useEffect(() => {
    useChatSessionStore.getState().hydrateSession();
    loadProfile();
  }, []);

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="h-screen flex flex-col">
        <div className="fixed top-4 left-4 z-10">
          <Button
            onClick={handleLogout}
          >
            Logout
          </Button>
        </div>
        <div className="flex-1 min-h-0">
          <Thread />
        </div>
      </div>
    </AssistantRuntimeProvider>
  );
};
