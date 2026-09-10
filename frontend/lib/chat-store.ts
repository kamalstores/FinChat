import { create } from "zustand";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type ChatSessionState = {
  sessionId: string | null;
  messages: Message[];

  setSessionId: (id: string) => void;
  hydrateSession: () => void;
};

export const useChatSessionStore = create<ChatSessionState>((set, get) => ({
  sessionId: null,
  messages: [],

  setSessionId: (id) => {
    localStorage.setItem("session_id", id);
    set({ sessionId: id });
  },

  getSessionId: () => {
    return get().sessionId;
  },

  hydrateSession: () => {
    localStorage.removeItem("session_id");
    set({ sessionId: null });
  },
}));