import json

import httpx

from google import genai
from google.genai import types

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


# =========================================
# AI PROVIDER
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
    ).strip()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return api_key


# =========================================
# GEMINI CONFIG
# =========================================

def get_gemini_config():
    return (
        types.GenerateContentConfig(
            system_instruction=
                SYSTEM_PROMPT,

            automatic_function_calling=
                types
                .AutomaticFunctionCallingConfig(
                    disable=True
                ),
        )
    )


# =========================================
# CONVERT HISTORY FOR GEMINI
# =========================================

def build_gemini_contents(
    messages: list[dict],
) -> list[types.Content]:

    contents = []

    for message in messages:

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

        # Gemini uses "model"
        # instead of "assistant".
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
# OLLAMA NON-STREAMING
# =========================================

async def generate_ollama_response(
    messages: list[dict],
) -> str:

    ollama_messages = [
        {
            "role": "system",
            "content":
                SYSTEM_PROMPT,
        }
    ]

    ollama_messages.extend(
        messages
    )

    payload = {
        "model":
            settings.OLLAMA_MODEL,

        "messages":
            ollama_messages,

        "stream":
            False,
    }

    async with httpx.AsyncClient(
        timeout=180.0
    ) as client:

        response = (
            await client.post(
                (
                    f"{settings.OLLAMA_BASE_URL}"
                    "/api/chat"
                ),
                json=payload,
            )
        )

        response.raise_for_status()

        data = response.json()

    return (
        data
        .get("message", {})
        .get("content", "")
    )


# =========================================
# GEMINI NON-STREAMING
# =========================================

async def generate_gemini_response(
    messages: list[dict],
) -> str:

    contents = (
        build_gemini_contents(
            messages
        )
    )

    client = genai.Client(
        api_key=
            get_gemini_api_key()
    )

    try:
        async with client.aio as aclient:

            response = (
                await aclient
                .models
                .generate_content(
                    model=
                        settings.GEMINI_MODEL,

                    contents=
                        contents,

                    config=
                        get_gemini_config(),
                )
            )

            return (
                response.text
                or ""
            )

    finally:
        client.close()


# =========================================
# MAIN NON-STREAMING
# =========================================

async def generate_ai_response(
    messages: list[dict],
) -> str:

    provider = (
        get_ai_provider()
    )

    if provider == "gemini":

        return await (
            generate_gemini_response(
                messages
            )
        )

    return await (
        generate_ollama_response(
            messages
        )
    )


# =========================================
# OLLAMA STREAMING
# =========================================

async def stream_ollama_response(
    messages: list[dict],
):

    ollama_messages = [
        {
            "role": "system",
            "content":
                SYSTEM_PROMPT,
        }
    ]

    ollama_messages.extend(
        messages
    )

    payload = {
        "model":
            settings.OLLAMA_MODEL,

        "messages":
            ollama_messages,

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

                data = json.loads(
                    line
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
# GEMINI STREAMING
# =========================================

async def stream_gemini_response(
    messages: list[dict],
):

    contents = (
        build_gemini_contents(
            messages
        )
    )

    client = genai.Client(
        api_key=
            get_gemini_api_key()
    )

    try:
        async with client.aio as aclient:

            stream = (
                await aclient
                .models
                .generate_content_stream(
                    model=
                        settings.GEMINI_MODEL,

                    contents=
                        contents,

                    config=
                        get_gemini_config(),
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
        client.close()


# =========================================
# MAIN STREAMING
# =========================================

async def stream_ai_response(
    messages: list[dict],
):

    provider = (
        get_ai_provider()
    )

    if provider == "gemini":

        async for chunk in (
            stream_gemini_response(
                messages
            )
        ):
            yield chunk

        return


    async for chunk in (
        stream_ollama_response(
            messages
        )
    ):
        yield chunk