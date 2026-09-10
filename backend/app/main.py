from fastapi import FastAPI
from app.api import routes
from fastapi.middleware.cors import CORSMiddleware
from app.agent.state import lifespan

app = FastAPI(title="RAG Chatbot", lifespan=lifespan)

for router in routes:
    app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# uvicorn app.main:app --reload
