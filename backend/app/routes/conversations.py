# Conversation list/open/delete routes will be implemented here.
from fastapi import APIRouter, HTTPException

from app.database import (
    conversations_collection,
    messages_collection,
)


router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


@router.get("")
async def get_conversations():
    conversations = []

    cursor = conversations_collection.find(
        {},
        {
            "_id": 0,
            "conversation_id": 1,
            "title": 1,
            "created_at": 1,
            "updated_at": 1,
        },
    ).sort("updated_at", -1)

    async for conversation in cursor:
        conversations.append(conversation)

    return conversations


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    conversation = await conversations_collection.find_one(
        {"conversation_id": conversation_id},
        {"_id": 0},
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = []

    cursor = messages_collection.find(
        {"conversation_id": conversation_id},
        {
            "_id": 0,
            "role": 1,
            "content": 1,
            "created_at": 1,
        },
    ).sort("created_at", 1)

    async for message in cursor:
        messages.append(message)

    return {
        "conversation_id": conversation_id,
        "title": conversation.get("title", "New Chat"),
        "messages": messages,
    }


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    await messages_collection.delete_many(
        {"conversation_id": conversation_id}
    )

    result = await conversations_collection.delete_one(
        {"conversation_id": conversation_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {
        "message": "Conversation deleted successfully"
    }