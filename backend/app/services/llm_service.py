import httpx

from app.config import settings


SYSTEM_PROMPT = """
You are Chatbot AI, a helpful and professional conversational AI assistant.

Rules:
- Give clear and useful responses.
- Remember previous conversation context.
- Keep answers easy to understand.
- Use Markdown when appropriate.
- Use code blocks for programming examples.
"""


async def generate_ai_response(messages: list[dict]) -> str:
    ollama_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    for message in messages:
        ollama_messages.append(
            {
                "role": message["role"],
                "content": message["content"],
            }
        )

    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": ollama_messages,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=payload,
        )

        response.raise_for_status()
        data = response.json()

    return data["message"]["content"]