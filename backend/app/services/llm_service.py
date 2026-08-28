import json

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


async def generate_ai_response(
    messages: list[dict],
) -> str:
    """
    Normal non-streaming response.
    Keeps the existing /api/chat endpoint working.
    """

    ollama_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    ollama_messages.extend(messages)

    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": ollama_messages,
        "stream": False,
    }

    async with httpx.AsyncClient(
        timeout=180.0
    ) as client:

        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

    return data["message"]["content"]


async def stream_ai_response(
    messages: list[dict],
):
    """
    Stream Ollama response token-by-token/chunk-by-chunk.
    """

    ollama_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    ollama_messages.extend(messages)

    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": ollama_messages,
        "stream": True,
    }

    async with httpx.AsyncClient(
        timeout=None
    ) as client:

        async with client.stream(
            "POST",
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=payload,
        ) as response:

            response.raise_for_status()

            async for line in response.aiter_lines():

                if not line:
                    continue

                data = json.loads(line)

                message = data.get(
                    "message",
                    {}
                )

                content = message.get(
                    "content",
                    ""
                )

                if content:
                    yield content

                if data.get("done"):
                    break