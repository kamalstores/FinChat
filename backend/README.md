# Chatbot Backend

FastAPI RAG chatbot with LangGraph agent, PostgreSQL persistence, and Pinecone vector store.

## Stack

- **API:** FastAPI (CORS, streaming)
- **AI:** LangChain, LangGraph, Google Gemini
- **Vector Store:** Pinecone (dense)
- **Database:** PostgreSQL 16 (SQLAlchemy, psycopg)
- **Auth:** JWT (pyjwt), Argon2 password hashing
- **Documents:** PyPDF ingestion + text splitting

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app, CORS, lifespan
│   ├── api/             # Route handlers
│   │   ├── auth.py      # POST /auth/register, /auth/login, /auth/logout
│   │   ├── chat.py      # POST /chat/generate, /chat/stream
│   │   ├── user.py      # GET /user
│   │   ├── sources.py   # GET /sources/{file_name}
│   │   └── health.py    # GET /health
│   ├── agent/           # LangGraph finance agent
│   │   ├── state.py     # App lifespan — agent + Postgres checkpointer init
│   │   ├── finance.py   # Agent graph definition
│   │   ├── services.py  # run_agent (sync/stream)
│   │   ├── grader.py    # Retrieval grader logic
│   │   ├── tools/       # Agent tools (retrieval, SQL, etc.)
│   │   ├── prompts/     # Prompt templates
│   │   └── provider/    # LLM and embedding provider config (Gemini)
│   ├── model/           # SQLAlchemy models (User, ChatSession, FinancialData)
│   ├── schema/          # Pydantic request/response schemas
│   ├── core/            # Config, security, logger
│   ├── shared/          # DB session, dependency injection, vector store client
│   └── scripts/         # Data ingestion pipeline
│       └── ingestion.py # Seed SQL data + embed documents into Pinecone
└── requirements.txt
```

## API Endpoints

| Method | Path               | Description              |
|--------|--------------------|--------------------------|
| POST   | `/auth/register`   | Create account           |
| POST   | `/auth/login`      | Login (returns JWT)      |
| POST   | `/auth/logout`     | Logout                   |
| POST   | `/chat/generate`   | Sync chat response       |
| POST   | `/chat/stream`     | Stream chat response     |
| GET    | `/user`            | Current user profile     |
| GET    | `/sources/{name}`  | Serve source PDF         |
| GET    | `/health`          | Health check             |

## Getting Started

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Requires PostgreSQL and Pinecone. Set `GEMINI_API_KEY`, `GEMINI_MODEL`, and
`GEMINI_EMBEDDING_MODEL` in `.env.local` (see `.env.example`).

## Docker

```bash
docker build -t backend .
docker run -p 8000:8000 backend
```

Or run the full stack via `docker-compose.yaml` from the project root.
