"""
models.py
---------
Pydantic schemas that define the shape of data going in and out of the API.
FastAPI uses these to validate requests and to auto-generate the
interactive docs at /docs.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(
        default=None,
        description="If omitted, a brand new conversation is created."
    )
    message: str = Field(..., min_length=1, description="The user's message text")


class MessageOut(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    created_at: datetime


class ConversationSummary(BaseModel):
    id: str
    title: str
    updated_at: datetime


class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: List[MessageOut]