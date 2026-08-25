# Chat API routes will be implemented here.
from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_chat


router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):

    try:
        result = await process_chat(
            conversation_id=request.conversation_id,
            message=request.message,
        )

        return ChatResponse(**result)

    except Exception as error:
        print(f"Chat error: {error}")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )