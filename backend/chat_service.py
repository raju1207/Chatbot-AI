"""
chat_service.py
----------------
This is the brain of the chatbot.

It:
1. Fetches recent conversation history from MongoDB.
2. Sends the history and new message to OpenAI.
3. Returns the AI-generated response.
"""

import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("API key loaded:", bool(api_key))

client = AsyncOpenAI(
    api_key=api_key
)

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)


# Maximum number of previous messages
MAX_HISTORY_MESSAGES = 20


# System prompt
SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant. "
    "Be clear and concise. "
    "If you don't know something, say so honestly."
)


async def get_recent_history(
    db,
    conversation_id: str
):
    """
    Fetch the last N messages for a conversation.
    Messages are returned in chronological order.
    """

    cursor = (
        db.messages
        .find(
            {
                "conversation_id": conversation_id
            }
        )
        .sort(
            "created_at",
            -1
        )
        .limit(
            MAX_HISTORY_MESSAGES
        )
    )

    docs = await cursor.to_list(
        length=MAX_HISTORY_MESSAGES
    )

    # Reverse to chronological order
    docs.reverse()

    return docs


async def generate_reply(
    db,
    conversation_id: str,
    user_message: str
) -> str:
    """
    Generate an AI reply using conversation history.
    """

    # Get previous messages
    history = await get_recent_history(
        db,
        conversation_id
    )

    # Start with system prompt
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Add conversation history
    for doc in history:

        messages.append(
            {
                "role": doc["role"],
                "content": doc["content"]
            }
        )

    # Add current user message
    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # Call OpenAI API
    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=800,
    )

    # Return AI response
    return response.choices[0].message.content.strip()


def make_title_from_message(
    message: str
) -> str:
    """
    Generate a short conversation title.
    """

    title = (
        message
        .strip()
        .split("\n")[0]
    )

    return (
        title[:40] + "…"
        if len(title) > 40
        else title
    )


def now_utc():
    """
    Return the current UTC datetime.
    """

    return datetime.now(
        timezone.utc
    )