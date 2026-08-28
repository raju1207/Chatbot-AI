import base64
import json

import httpx

from google import genai
from google.genai import types

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


# =========================================
# PROVIDER
# =========================================

def get_ai_provider() -> str:
    provider = (
        settings.AI_PROVIDER
        .strip()
        .lower()
    )

    if provider not in {
        "ollama",
        "gemini",
    }:
        raise ValueError(
            "AI_PROVIDER must be "
            "'ollama' or 'gemini'."
        )

    return provider


# =========================================
# GEMINI API KEY
# =========================================

def get_gemini_api_key() -> str:
    api_key = (
        settings.GEMINI_API_KEY
        or ""
    )

    api_key = (
        api_key.strip()
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return api_key


# =========================================
# IMAGE ENCODING FOR OLLAMA
# =========================================

def encode_image(
    image_bytes: bytes,
) -> str:

    return (
        base64
        .b64encode(
            image_bytes
        )
        .decode(
            "utf-8"
        )
    )


# =========================================
# GEMINI CHAT HISTORY
# =========================================

def build_gemini_history(
    history: list[dict] | None,
) -> list[types.Content]:

    contents = []

    if not history:
        return contents

    for message in history:

        text = str(
            message.get(
                "content",
                "",
            )
        ).strip()

        if not text:
            continue

        source_role = (
            message.get(
                "role",
                "user",
            )
        )

        role = (
            "model"
            if source_role == "assistant"
            else "user"
        )

        contents.append(
            types.Content(
                role=role,

                parts=[
                    types.Part.from_text(
                        text=text
                    )
                ],
            )
        )

    return contents


# =========================================
# OLLAMA VISION
# =========================================

async def stream_ollama_vision_response(
    prompt: str,
    image_bytes: bytes,
    history: list[dict] | None,
):

    encoded_image = (
        encode_image(
            image_bytes
        )
    )

    messages = [
        {
            "role": "system",

            "content":
                VISION_SYSTEM_PROMPT,
        }
    ]

    if history:
        messages.extend(
            history
        )

    messages.append(
        {
            "role": "user",

            "content":
                prompt,

            "images": [
                encoded_image
            ],
        }
    )

    payload = {
        "model":
            settings
            .OLLAMA_VISION_MODEL,

        "messages":
            messages,

        "stream":
            True,
    }

    async with httpx.AsyncClient(
        timeout=None
    ) as client:

        async with client.stream(
            "POST",
            (
                f"{settings.OLLAMA_BASE_URL}"
                "/api/chat"
            ),
            json=payload,
        ) as response:

            response.raise_for_status()

            async for line in (
                response.aiter_lines()
            ):

                if not line:
                    continue

                data = (
                    json.loads(line)
                )

                content = (
                    data
                    .get(
                        "message",
                        {},
                    )
                    .get(
                        "content",
                        "",
                    )
                )

                if content:
                    yield content

                if data.get("done"):
                    break


# =========================================
# GEMINI VISION
# =========================================

async def stream_gemini_vision_response(
    prompt: str,
    image_bytes: bytes,
    mime_type: str,
    history: list[dict] | None,
):

    contents = (
        build_gemini_history(
            history
        )
    )

    image_part = (
        types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )
    )

    user_content = (
        types.Content(
            role="user",

            parts=[
                types.Part.from_text(
                    text=prompt
                ),

                image_part,
            ],
        )
    )

    contents.append(
        user_content
    )

    client = (
        genai.Client(
            api_key=
                get_gemini_api_key()
        )
    )

    async_client = (
        client.aio
    )

    try:
        stream = (
            await async_client
            .models
            .generate_content_stream(
                model=
                    settings
                    .GEMINI_VISION_MODEL,

                contents=
                    contents,

                config=
                    types
                    .GenerateContentConfig(
                        system_instruction=
                            VISION_SYSTEM_PROMPT,
                    ),
            )
        )

        async for chunk in stream:

            text = (
                chunk.text
                or ""
            )

            if text:
                yield text

    finally:
        await (
            async_client
            .aclose()
        )

        client.close()


# =========================================
# MAIN VISION FUNCTION
# =========================================

async def stream_vision_response(
    prompt: str,
    image_bytes: bytes,
    history: list[dict] | None = None,
    mime_type: str = "image/jpeg",
):

    provider = (
        get_ai_provider()
    )

    if provider == "gemini":

        async for chunk in (
            stream_gemini_vision_response(
                prompt=prompt,

                image_bytes=
                    image_bytes,

                mime_type=
                    mime_type,

                history=
                    history,
            )
        ):
            yield chunk

        return


    async for chunk in (
        stream_ollama_vision_response(
            prompt=prompt,

            image_bytes=
                image_bytes,

            history=
                history,
        )
    ):
        yield chunk