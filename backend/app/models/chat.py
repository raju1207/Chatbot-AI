from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(
        min_length=1,
        max_length=10000,
    )


class ChatResponse(BaseModel):
    conversation_id: str
    response: str


class RegenerateRequest(BaseModel):
    conversation_id: str = Field(
        min_length=1
    )