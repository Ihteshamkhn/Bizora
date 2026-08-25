"""AI chat API endpoint."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai.agent import ask_agent
from api.deps import get_business_owned
from database.connection import get_db
from database.models import Business

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    history: list[dict] | None = None  # [{"role": "user"|"assistant", "content": "..."}]


@router.post("/{business_id}")
def chat(body: ChatRequest,
         business: Business = Depends(get_business_owned),
         db: Session = Depends(get_db)):
    if not body.question.strip():
        from fastapi import HTTPException
        raise HTTPException(400, "Question cannot be empty")
    return ask_agent(db, business.id, body.question.strip(), body.history)
