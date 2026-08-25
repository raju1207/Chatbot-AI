# Chat orchestration and MongoDB persistence will be implemented here.
from datetime import datetime, timezone
from uuid import uuid4

from app.database import (
    conversations_collection,
    messages_collection,
)
from app.services.llm_service import generate_ai_response


async def create_conversation() -> str:
    conversation_id = str(uuid4())

    await conversations_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "title": "New Chat",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    return conversation_id


async def get_conversation_history(
    conversation_id: str,
    limit: int = 20,
) -> list[dict]:

    cursor = (
        messages_collection
        .find(
            {"conversation_id": conversation_id},
            {
                "_id": 0,
                "role": 1,
                "content": 1,
                "created_at": 1,
            },
        )
        .sort("created_at", -1)
        .limit(limit)
    )

    messages = []

    async for message in cursor:
        messages.append(
            {
                "role": message["role"],
                "content": message["content"],
            }
        )

    messages.reverse()

    return messages


async def process_chat(
    conversation_id: str | None,
    message: str,
) -> dict:

    if not conversation_id:
        conversation_id = await create_conversation()

    # Save user message
    await messages_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "role": "user",
            "content": message,
            "created_at": datetime.now(timezone.utc),
        }
    )

    # Read recent conversation history
    history = await get_conversation_history(
        conversation_id=conversation_id,
        limit=20,
    )

    # Generate AI response
    ai_response = await generate_ai_response(history)

    # Save assistant message
    await messages_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": ai_response,
            "created_at": datetime.now(timezone.utc),
        }
    )

    # Update conversation metadata
    await conversations_collection.update_one(
        {"conversation_id": conversation_id},
        {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        },
    )

    return {
        "conversation_id": conversation_id,
        "response": ai_response,
    }