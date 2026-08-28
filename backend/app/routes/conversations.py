from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.database import (
    conversations_collection,
    messages_collection,
)

from app.services.auth_service import (
    get_current_user,
)


router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


# =========================================
# GET ALL CONVERSATIONS FOR LOGGED-IN USER
# =========================================

@router.get("")
async def get_conversations(
    current_user=Depends(
        get_current_user
    ),
):
    user_id = current_user[
        "user_id"
    ]

    cursor = (
        conversations_collection
        .find(
            {
                "user_id": user_id
            },
            {
                "_id": 0
            },
        )
        .sort(
            "updated_at",
            -1,
        )
    )

    conversations = []

    async for conversation in cursor:
        conversations.append(
            conversation
        )

    return conversations


# =========================================
# GET ONE CONVERSATION
# =========================================

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,

    current_user=Depends(
        get_current_user
    ),
):
    user_id = current_user[
        "user_id"
    ]

    conversation = (
        await conversations_collection
        .find_one(
            {
                "conversation_id":
                    conversation_id,

                "user_id":
                    user_id,
            },
            {
                "_id": 0
            },
        )
    )

    # Important:
    # User cannot know whether another
    # user's conversation exists.
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=
                "Conversation not found.",
        )

    cursor = (
        messages_collection
        .find(
            {
                "conversation_id":
                    conversation_id
            },
            {
                "_id": 0
            },
        )
        .sort(
            "created_at",
            1,
        )
    )

    messages = []

    async for message in cursor:
        messages.append(
            message
        )

    return {
        **conversation,
        "messages": messages,
    }


# =========================================
# DELETE CONVERSATION
# =========================================

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,

    current_user=Depends(
        get_current_user
    ),
):
    user_id = current_user[
        "user_id"
    ]

    # First make sure this chat
    # belongs to logged-in user.
    conversation = (
        await conversations_collection
        .find_one(
            {
                "conversation_id":
                    conversation_id,

                "user_id":
                    user_id,
            }
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=
                "Conversation not found.",
        )

    await conversations_collection.delete_one(
        {
            "conversation_id":
                conversation_id,

            "user_id":
                user_id,
        }
    )

    await messages_collection.delete_many(
        {
            "conversation_id":
                conversation_id
        }
    )

    return {
        "message":
            "Conversation deleted successfully."
    }