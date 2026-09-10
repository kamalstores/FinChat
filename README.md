# FinChat

FinChat is a financial question-answering application. It lets a user ask questions in a chat interface and receive answers grounded in structured financial data and company 10-K filings.

It is built for questions such as:

- "What was Apple's revenue in 2024?"
- "Compare Apple's revenue with Microsoft's revenue from 2022 to 2025."
- "What business risks does Amazon describe in its filing?"
- "What happened to Meta's net income, and what explanation is available in its filing?"

This project is a learning-friendly example of combining a web application, an LLM, SQL, retrieval-augmented generation (RAG), vector search, authentication, and streaming responses.

## Contents

- [What the project does](#what-the-project-does)
- [Why it is different from a normal chatbot](#why-it-is-different-from-a-normal-chatbot)
- [Main advantages](#main-advantages)
- [Architecture](#architecture)
- [Technology](#technology)
- [Data coverage and limitations](#data-coverage-and-limitations)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Run with Docker Compose](#run-with-docker-compose-recommended)
- [Run services locally](#run-services-locally)
- [Run only the backend](#run-only-the-backend)
- [Useful commands](#useful-commands)
- [API endpoints](#api-endpoints)
- [Example questions](#example-questions)
- [How the answer is produced](#how-the-answer-is-produced)
- [Troubleshooting](#troubleshooting)
- [Project structure](#project-structure)
- [Security notes](#security-notes)

## What the project does

FinChat has two ways to find information:

1. **SQL lookup for numerical data**
	 - Reads financial records from PostgreSQL.
	 - Handles revenue, gross profit, operating income, and net income.
	 - Supports years from 2022 to 2025 in the included dataset.
	 - Works well for comparisons, trends, rankings, and calculations.

2. **RAG search for filing text**
	 - Searches the text of company 10-K filings in Pinecone.
	 - Uses Gemini embeddings to find relevant passages.
	 - Uses a relevance grader to filter weak matches.
	 - Returns source documents and page references when filing evidence is used.

The Gemini model decides which tool is appropriate. The LangGraph workflow can call a tool, inspect its result, call another tool, and then write the final answer.

## Why it is different from a normal chatbot

A normal chatbot can answer from general model knowledge. That is often unsuitable for financial questions because the answer may be outdated, unsupported, or invented.

FinChat is different because:

- Numerical questions are answered from a database instead of model memory.
- Qualitative questions are answered from retrieved filing passages.
- The assistant is instructed not to invent missing financial information.
- SQL and filing evidence can be combined for a single question.
- Filing answers can include a document and page link.
- User accounts and chat sessions are stored securely in the backend.
- Responses can stream progressively to the browser.

The chat screen is intentionally familiar. The specialization is in the backend tools, data, retrieval rules, and source grounding.

## Main advantages

### More reliable numerical answers

The model does not need to remember Apple's revenue. It calls `sql_query`, which reads the value from PostgreSQL.

### Better financial research

The SQL database answers "what happened?" Filing search helps answer "why did it happen?" or "what risks does the company report?"

### Evidence instead of unsupported claims

The application can display the SQL result and filing sources used for the answer. This makes the answer easier to inspect.

### Tool-based design

The SQL and RAG tools are separate. This makes the project easier to extend with tools such as market data, SEC filing updates, portfolio analysis, or financial ratios.

### Local development

PostgreSQL and Pinecone Local can run in Docker. The application can also be developed with the backend and frontend running directly on your computer.

## Architecture

```text
Browser
	|
	v
Next.js frontend (:3000)
	|
	v
FastAPI backend (:8000)
	|
	v
LangGraph financial agent
	|                  |
	|                  +--> SQL tool --> PostgreSQL
	|
	+--> RAG tool --> Gemini embeddings --> Pinecone
												 |
												 +--> Gemini Flash for answer and grading

PostgreSQL also stores users and chat-session checkpoints.
```

### Request flow

1. The user signs up or logs in.
2. The frontend sends the question and JWT token to the backend.
3. The LangGraph agent chooses SQL, RAG, or both.
4. SQL reads structured financial records from PostgreSQL.
5. RAG searches embedded 10-K text in Pinecone and grades the matches.
6. Gemini writes an answer using the tool results.
7. The backend streams the answer, tool calls, and sources to the frontend.

## Technology

| Area | Technology |
| --- | --- |
| Frontend | Next.js 16, React, TypeScript, assistant-ui, Tailwind CSS |
| Backend | FastAPI, Python 3.11, SQLAlchemy |
| Agent | LangChain, LangGraph, Google Gemini |
| Chat model | Configurable Gemini Flash model |
| Embeddings | `gemini-embedding-001`, configured for 512 dimensions |
| Relational database | PostgreSQL 16 |
| Vector database | Pinecone Local for development |
| Authentication | JWT and Argon2 password hashing |
| Persistence | PostgreSQL chat-session checkpointing |
| Containers | Docker and Docker Compose |

## Data coverage and limitations

The included data is a demonstration dataset, not a live market-data service.

- SQL financial data covers the years 2022 through 2025 in the included seed files.
- The RAG filing dataset currently contains FY2025 filings for Apple, Amazon, Alphabet, and Meta.
- RAG company names allowed by the application are Apple, Amazon, Alphabet, and Meta.
- Google is normalized to Alphabet, and Facebook is normalized to Meta.
- The application does not provide live stock prices, real-time news, investment advice, or guaranteed future forecasts.
- It should not be used as the sole basis for an investment decision.
- A question outside the available data should receive a data-not-available response rather than an invented answer.

## Prerequisites

For the recommended Docker setup:

- Docker Desktop with Docker Compose
- A Google AI Studio Gemini API key
- Internet access the first time images and Python packages are built

For local application development:

- Python 3.11 or newer
- Node.js 22 or newer
- npm
- Docker, PostgreSQL, and Pinecone Local, or equivalent running services

## Configuration

Create the environment file from the template:

```bash
cp .env.example .env
```

Open `.env` and set at least:

```env
SECRET_KEY=replace_with_a_long_random_value
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

The default configuration is for Docker Compose:

```env
DB_HOST=db
DB_PORT=5432
PINECONE_HOST=http://pinecone:8000
PINECONE_INDEX_HOST=http://host.docker.internal:5081
PINECONE_API_KEY=pclocal
PINECONE_INDEX_NAME=finchat
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Use the exact Gemini model identifier available to your Google AI Studio project. The repository default is `gemini-2.5-flash`; model availability can change by account and region.

Do not commit `.env` or expose `GEMINI_API_KEY` in frontend code. The repository ignores `.env`.

## Run with Docker Compose (recommended)

This is the easiest way to run the complete application.

### 1. Start the stack

From the repository root:

```bash
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
docker compose up --build
```

The first build can take several minutes.

### 2. Open the application

Open [http://localhost:3000](http://localhost:3000), create an account, and start asking questions.

The backend API is available at [http://localhost:8000](http://localhost:8000). FastAPI documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. What Compose starts

| Service | Port | Purpose |
| --- | --- | --- |
| `db` | 5432 | PostgreSQL database and seeded SQL data |
| `pinecone` | 5080-5081 | Local vector database |
| `ingestion` | none | Re-embeds documents and seeds Pinecone once |
| `backend` | 8000 | FastAPI API and financial agent |
| `frontend` | 3000 | Next.js web application |

The `ingestion` service runs:

1. `app.scripts.re_embed` to generate 512-dimensional Gemini embeddings.
2. `app.scripts.ingestion` to create the Pinecone index and upload vectors and users.

This is important when changing embedding providers. Existing OpenAI vectors must not be mixed with Gemini query embeddings.

### Stop the stack

Press `Ctrl+C` for a foreground run, or use:

```bash
docker compose down
```

To remove the PostgreSQL volume and start with a completely fresh database:

```bash
docker compose down -v
```

Use `down -v` carefully because it deletes local database data.

## Run services locally

This mode is useful when actively changing Python or TypeScript code. Run PostgreSQL and Pinecone Local in Docker, then run the applications on the host.

### 1. Start only infrastructure

The Compose file also defines the application services, so start the infrastructure services directly:

```bash
docker compose up db pinecone
```

Leave this terminal running.

### 2. Create local backend configuration

Copy the template to the filename used by the backend when running outside Docker:

```bash
cp .env.example backend/.env.local
```

Edit `backend/.env.local` for host access:

```env
DB_HOST=localhost
PINECONE_HOST=http://localhost:5080
PINECONE_INDEX_HOST=http://localhost:5081
```

Keep your Gemini key and other values in this file. Do not commit it.

### 3. Install and run the backend

In a new terminal:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.scripts.re_embed
python -m app.scripts.ingestion
uvicorn app.main:app --reload
```

The backend runs at [http://localhost:8000](http://localhost:8000).

### 4. Install and run the frontend

In another terminal:

```bash
cd frontend
npm install
printf 'NEXT_PUBLIC_API_URL=http://localhost:8000\n' > .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Run only the backend

Use this when the frontend is already running or when testing the API with Swagger or curl.

Start PostgreSQL and Pinecone first, configure `backend/.env.local`, then:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Check that it is running:

```bash
curl http://localhost:8000/health/
```

Expected response:

```json
{"status":"ok"}
```

## Useful commands

### Docker logs

```bash
docker compose logs -f backend
docker compose logs -f ingestion
docker compose logs -f frontend
```

### Rebuild one service

```bash
docker compose build backend
docker compose up backend
```

### Inspect running containers

```bash
docker compose ps
```

### Re-run ingestion

```bash
docker compose run --rm ingestion
```

This calls Gemini and may use API quota because it regenerates all document embeddings.

### Compile the backend

```bash
python3 -m compileall -q backend/app
```

## API endpoints

The main endpoints are:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Create a user and receive a JWT |
| `POST` | `/auth/login` | Log in with username and password |
| `POST` | `/auth/logout` | Return a logout confirmation |
| `POST` | `/chat/generate` | Generate a complete response |
| `POST` | `/chat/stream` | Stream response, tool calls, and sources as NDJSON |
| `GET` | `/user/` | Read the current user profile |
| `GET` | `/sources/{file_name}` | Serve a filing PDF |
| `GET` | `/health/` | Check API availability |

Interactive API documentation is available at `/docs` while the backend is running.

### Example registration

```bash
curl -X POST http://localhost:8000/auth/register \
	-H 'Content-Type: application/json' \
	-d '{"username":"demo","password":"change-this-password"}'
```

### Example login

```bash
curl -X POST http://localhost:8000/auth/login \
	-H 'Content-Type: application/x-www-form-urlencoded' \
	-d 'username=demo&password=change-this-password'
```

Use the returned access token as:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Example questions

### SQL questions

- What was Apple's revenue in 2024?
- Show Microsoft's revenue from 2022 to 2025.
- Compare Apple and Amazon's net income in 2024.
- Which company had the highest operating income in 2025?
- What was the change in Apple's revenue between 2023 and 2024?

### Filing questions

- What are Apple's main business risks?
- What does Amazon's filing say about AWS?
- What competition risks does Alphabet describe?
- What regulatory risks does Meta report?

### Combined questions

- What happened to Apple's revenue between 2023 and 2024, and what does its filing say about the business context?
- Compare Amazon's 2024 financial performance with the risks described in its filing.
- What happened to Meta's net income, and what filing evidence helps explain it?

### Boundary tests

- What was Apple's revenue in 2020? The included SQL data may not cover this year.
- What is Apple's stock price today? This application has no live market-price tool.
- What is the best stock to buy? This application is not an investment advisor.
- What are Tesla's 2025 filing risks? Tesla is not in the included RAG filing dataset.

## How the answer is produced

### Numerical question

For "What was Apple's revenue in 2024?":

1. Gemini selects `sql_query`.
2. The tool validates the company, metric, and year range.
3. SQLAlchemy queries PostgreSQL.
4. The result is returned to the agent.
5. Gemini formats the answer.
6. The frontend shows the tool call and SQL-backed source output.

### Filing question

For "What are Apple's main business risks?":

1. Gemini selects `rag_search`.
2. The question is embedded with Gemini.
3. Pinecone finds similar filing chunks.
4. Results below the relevance threshold are removed.
5. A second Gemini call grades the remaining documents.
6. The best passages and page metadata are returned.
7. The frontend displays the answer and filing links.

### Combined question

The LangGraph agent can call SQL for the numbers and RAG for the explanation before producing one grounded response.

## Troubleshooting

### The backend cannot start because a setting is missing

Check that `.env` exists for Docker or `backend/.env.local` exists for a local backend. Confirm that `GEMINI_API_KEY`, database settings, and Pinecone settings are present.

### Gemini authentication fails

Check the key in `.env`, confirm that it is active in Google AI Studio, and verify that `GEMINI_MODEL` is available to your account.

### Pinecone reports a dimension mismatch

The index must use dimension `512`, matching the embedding configuration. Recreate local data and run ingestion again:

```bash
docker compose down -v
docker compose up --build
```

### The app starts but filing search returns nothing

Confirm that the `ingestion` service completed successfully. Check:

```bash
docker compose logs ingestion
```

Also verify that the question names one of the supported RAG companies: Apple, Amazon, Alphabet, or Meta.

### The frontend cannot connect to the backend

Confirm that the backend is running on port 8000 and that `NEXT_PUBLIC_API_URL` is set to:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Restart the frontend after changing this value.

### Docker containers already exist

Use:

```bash
docker compose down
docker compose up --build
```

Use `docker compose down -v` only when you intentionally want to delete the local PostgreSQL volume.

## Project structure

```text
FinChat/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── finance.py          # LangGraph workflow
│   │   │   ├── grader.py           # Filing relevance grader
│   │   │   ├── services.py         # Sync and streaming execution
│   │   │   ├── provider/gemini.py  # Gemini chat and embeddings
│   │   │   ├── tools/sql.py        # Structured financial queries
│   │   │   └── tools/rag.py        # Filing retrieval
│   │   ├── api/                    # FastAPI routes
│   │   ├── core/                   # Settings, security, logging
│   │   ├── model/                  # SQLAlchemy database models
│   │   ├── scripts/                # Re-embedding and ingestion jobs
│   │   └── shared/                 # Database and Pinecone clients
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                        # Next.js pages and runtime
│   ├── components/                 # Chat and UI components
│   ├── service/                    # Backend API clients
│   ├── package.json
│   └── Dockerfile
├── .env.example                    # Configuration template
└── docker-compose.yaml             # Full local stack
```

## Security notes

- Use a long random `SECRET_KEY` outside local demonstrations.
- Never commit `.env`, API keys, passwords, or production database credentials.
- The included default database credentials are for local development only.
- Use HTTPS, secure cookie/token handling, proper secret management, and a production database before deploying publicly.
- This project provides financial information, not personalized investment advice.

## License and data notice

This repository is a development and demonstration project. Review the licenses and terms for any financial documents, model APIs, datasets, and third-party services before redistributing or deploying it commercially.
