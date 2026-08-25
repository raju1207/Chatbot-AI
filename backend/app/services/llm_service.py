# OpenAI integration will be implemented here.
from openai import AsyncOpenAI

from app.config import settings


client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY
)


SYSTEM_PROMPT = """
You are Chatbot AI, a helpful, professional conversational AI assistant.

Rules:
- Give clear and useful responses.
- Remember the context supplied from earlier messages.
- Format technical answers clearly.
- Use code blocks when appropriate.
- Do not claim information that is not available in the conversation.
"""


async def generate_ai_response(messages: list[dict]) -> str:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is missing from .env")

    conversation_text = []

    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")

        conversation_text.append(
            f"{role.upper()}: {content}"
        )

    prompt = "\n\n".join(conversation_text)

    response = await client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=prompt,
    )

    return response.output_text