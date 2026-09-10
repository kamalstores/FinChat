# Chatbot Frontend

Next.js 16 AI-powered chatbot UI with streaming responses, authentication, and a modern component library.

## Stack

- **Framework:** Next.js 16 (Turbopack, App Router, standalone output)
- **AI:** assistant-ui + Vercel AI SDK (streaming chat)
- **UI:** shadcn/ui, Radix Primitives, Tailwind CSS 4, Lucide icons
- **State:** Zustand (auth profile, chat sessions)
- **Auth:** JWT-based (stored in `localStorage`)
- **Notifications:** Sonner toast

## Project Structure

```
frontend/
├── app/              # Next.js App Router pages
│   ├── layout.tsx    # Root layout (dark theme, fonts, providers)
│   ├── page.tsx      # Home — redirects to /login if unauthenticated
│   ├── assistant.tsx # Chat runtime provider + thread
│   ├── login/        # Login page
│   └── sign-up/      # Registration page
├── components/
│   ├── assistant-ui/ # Thread, message components, tool UI
│   └── ui/           # shadcn/ui primitives (button, dialog, etc.)
├── lib/              # Auth utils, Zustand stores, Tailwind helpers
├── service/          # API client (chat, stream, auth, user)
└── hooks/            # Custom hooks (use-mobile)
```

## API Integration

All API calls go through `service/` modules:
- `chat.ts` / `stream.ts` — chat messages (blocking & SSE streaming)
- `login.ts` / `register.ts` — authentication
- `user.ts` — user profile fetch

## Getting Started

```bash
npm install
npm run dev
```

Requires the backend to be running. Set `NEXT_PUBLIC_API_URL` in `.env.local`.

## Docker

Built as a standalone Next.js image. See `Dockerfile` in this directory or run via `docker compose` from the project root.
