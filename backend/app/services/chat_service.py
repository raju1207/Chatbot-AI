from datetime import datetime, timezone
from uuid import uuid4

from app.database import (
    conversations_collection,
    messages_collection,
)

from app.services.llm_service import (
    generate_ai_response,
)


def generate_title(message: str) -> str:
    message = message.strip()

    if len(message) <= 40:
        return message

    return message[:40] + "..."


async def get_owned_conversation(
    conversation_id: str,
    user_id: str,
):
    """
    Return a conversation only when it belongs
    to the authenticated user.
    """

    conversation = (
        await conversations_collection.find_one(
            {
                "conversation_id": conversation_id,
                "user_id": user_id,
            }
        )
    )

    return conversation


async def verify_conversation_owner(
    conversation_id: str,
    user_id: str,
):
    conversation = await get_owned_conversation(
        conversation_id,
        user_id,
    )

    if not conversation:
        # Do not reveal whether another user owns it.
        raise ValueError(
            "Conversation not found."
        )

    return conversation


async def create_conversation(
    first_message: str,
    user_id: str,
) -> str:
    conversation_id = str(uuid4())

    now = datetime.now(
        timezone.utc
    )

    await conversations_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "title": generate_title(
                first_message
            ),
            "created_at": now,
            "updated_at": now,
        }
    )

    return conversation_id


async def save_user_message(
    conversation_id: str,
    message: str,
):
    await messages_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "role": "user",
            "content": message,
            "created_at": datetime.now(
                timezone.utc
            ),
        }
    )


async def save_assistant_message(
    conversation_id: str,
    message: str,
):
    await messages_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": message,
            "created_at": datetime.now(
                timezone.utc
            ),
        }
    )

    await conversations_collection.update_one(
        {
            "conversation_id": conversation_id,
        },
        {
            "$set": {
                "updated_at": datetime.now(
                    timezone.utc
                )
            }
        },
    )


async def replace_assistant_message(
    message_id,
    conversation_id: str,
    message: str,
):
    await messages_collection.update_one(
        {
            "_id": message_id,
            "conversation_id": conversation_id,
        },
        {
            "$set": {
                "content": message,
                "created_at": datetime.now(
                    timezone.utc
                ),
            }
        },
    )

    await conversations_collection.update_one(
        {
            "conversation_id": conversation_id,
        },
        {
            "$set": {
                "updated_at": datetime.now(
                    timezone.utc
                )
            }
        },
    )


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
        .sort(
            "created_at",
            -1,
        )
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


async def prepare_chat(
    conversation_id: str | None,
    message: str,
    user_id: str,
):
    if not conversation_id:
        conversation_id = (
            await create_conversation(
                message,
                user_id,
            )
        )

    else:
        await verify_conversation_owner(
            conversation_id,
            user_id,
        )

    await save_user_message(
        conversation_id,
        message,
    )

    history = (
        await get_conversation_history(
            conversation_id,
            limit=20,
        )
    )

    return (
        conversation_id,
        history,
    )


async def prepare_regeneration(
    conversation_id: str,
    user_id: str,
):
    await verify_conversation_owner(
        conversation_id,
        user_id,
    )

    cursor = (
        messages_collection
        .find(
            {
                "conversation_id": conversation_id
            }
        )
        .sort(
            "created_at",
            -1,
        )
        .limit(1)
    )

    latest_message = None

    async for item in cursor:
        latest_message = item
        break

    if not latest_message:
        raise ValueError(
            "Conversation has no messages."
        )

    if (
        latest_message.get("role")
        != "assistant"
    ):
        raise ValueError(
            "There is no completed assistant response to regenerate."
        )

    assistant_message_id = (
        latest_message["_id"]
    )

    cursor = (
        messages_collection
        .find(
            {
                "conversation_id":
                    conversation_id,

                "_id": {
                    "$ne":
                        assistant_message_id
                },
            },
            {
                "_id": 0,
                "role": 1,
                "content": 1,
                "created_at": 1,
            },
        )
        .sort(
            "created_at",
            -1,
        )
        .limit(20)
    )

    history = []

    async for message in cursor:
        history.append(
            {
                "role":
                    message["role"],

                "content":
                    message["content"],
            }
        )

    history.reverse()

    if (
        not history
        or history[-1]["role"]
        != "user"
    ):
        raise ValueError(
            "Could not find the user message to regenerate."
        )

    return (
        conversation_id,
        history,
        assistant_message_id,
    )


async def process_chat(
    conversation_id: str | None,
    message: str,
    user_id: str,
) -> dict:
    (
        conversation_id,
        history,
    ) = await prepare_chat(
        conversation_id,
        message,
        user_id,
    )

    ai_response = (
        await generate_ai_response(
            history
        )
    )

    await save_assistant_message(
        conversation_id,
        ai_response,
    )

    return {
        "conversation_id":
            conversation_id,

        "response":
            ai_response,
    }