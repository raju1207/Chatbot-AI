from fastapi import APIRouter
from app.models import ChatRequest, ChatResponse
from app.chat_service import generate_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer = await generate_response(
        request.conversation_id,
        request.message
    )

    return ChatResponse(response=answer)