from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.database import messages

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are a professional AI assistant. Give clear, accurate, and concise answers."
)

async def generate_response(conversation_id: str, user_message: str):
    history = []

    async for msg in messages.find(
        {"conversation_id": conversation_id}
    ).sort("created_at", 1):
        history.append(
            {
                "role": msg["role"],
                "content": msg["content"]
            }
        )

    history.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *history
        ],
        temperature=0.7
    )

    assistant_message = response.choices[0].message.content

    return assistant_message