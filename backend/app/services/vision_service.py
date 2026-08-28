# Image understanding logic will be implemented here.

import base64
import json

import httpx

from app.config import settings


VISION_SYSTEM_PROMPT = """
You are Chatbot AI with image understanding capabilities.

Analyze the provided image carefully.

Rules:
- Answer the user's question about the image.
- Describe only what can reasonably be observed.
- Do not invent details.
- If text is visible in the image, explain it when relevant.
- Keep answers clear and professional.
- Use Markdown when useful.
"""


def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(
        image_bytes
    ).decode("utf-8")


async def stream_vision_response(
    prompt: str,
    image_bytes: bytes,
    history: list[dict] | None = None,
):
    encoded_image = encode_image(
        image_bytes
    )

    messages = [
        {
            "role": "system",
            "content": VISION_SYSTEM_PROMPT,
        }
    ]

    if history:
        messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": prompt,
            "images": [
                encoded_image
            ],
        }
    )

    payload = {
        "model":
            settings.OLLAMA_VISION_MODEL,

        "messages":
            messages,

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

            async for line in (
                response.aiter_lines()
            ):

                if not line:
                    continue

                data = json.loads(line)

                content = (
                    data
                    .get("message", {})
                    .get("content", "")
                )

                if content:
                    yield content

                if data.get("done"):
                    break