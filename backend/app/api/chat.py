from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agent.services import run_agent
from app.model.user import User
from app.schema.chat import ChatRequest
from app.shared.dependencies import get_current_user, get_db

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/generate")
def generate(app_request: Request, request: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = app_request.app.state.agent
    request.stream = False
    return run_agent(agent, request, user, db)

@router.post("/stream")
def stream(app_request: Request, request: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = app_request.app.state.agent
    request.stream = True
    return StreamingResponse(
        run_agent(agent, request, user, db),
        media_type="application/x-ndjson",
    )