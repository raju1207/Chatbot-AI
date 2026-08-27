# Chat orchestration and MongoDB persistence will be implemented here.

from datetime import datetime, timezone
from uuid import uuid4

from app.database import (
    conversations_collection,
    messages_collection,
)

from app.services.llm_service import generate_ai_response


def generate_title(message: str) -> str:
    message = message.strip()

    if len(message) <= 40:
        return message

    return message[:40] + "..."


async def create_conversation(
    first_message: str,
) -> str:

    conversation_id = str(uuid4())

    await conversations_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "title": generate_title(first_message),
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
            {
                "conversation_id": conversation_id
            },
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
        conversation_id = await create_conversation(
            message
        )

    await messages_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "role": "user",
            "content": message,
            "created_at": datetime.now(timezone.utc),
        }
    )

    history = await get_conversation_history(
        conversation_id=conversation_id,
        limit=20,
    )

    ai_response = await generate_ai_response(
        history
    )

    await messages_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": ai_response,
            "created_at": datetime.now(timezone.utc),
        }
    )

    await conversations_collection.update_one(
        {
            "conversation_id": conversation_id
        },
        {
            "$set": {
                "updated_at": datetime.now(
                    timezone.utc
                )
            }
        },
    )

    return {
        "conversation_id": conversation_id,
        "response": ai_response,
    }