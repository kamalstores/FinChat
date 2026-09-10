from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.shared.db import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
