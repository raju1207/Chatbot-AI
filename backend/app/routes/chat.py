import asyncio
import json

from fastapi import (
    APIRouter,
    HTTPException,
)

from fastapi.responses import (
    StreamingResponse,
)

from app.models.chat import (
    ChatRequest,
    ChatResponse,
    RegenerateRequest,
)

from app.services.chat_service import (
    prepare_chat,
    prepare_regeneration,
    process_chat,
    replace_assistant_message,
    save_assistant_message,
)

from app.services.llm_service import (
    stream_ai_response,
)


router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
):

    try:

        result = await process_chat(
            conversation_id=
                request.conversation_id,

            message=
                request.message,
        )

        return ChatResponse(
            **result
        )

    except Exception as error:

        print(
            "Chat error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


async def create_stream(
    conversation_id: str,
    history: list[dict],
    replace_message_id=None,
):
    """
    Shared streaming logic for:
    - new message
    - regenerate response
    """

    full_response = ""

    yield (
        json.dumps(
            {
                "type": "meta",

                "conversation_id":
                    conversation_id,
            }
        )
        + "\n"
    )


    try:

        async for chunk in (
            stream_ai_response(
                history
            )
        ):

            full_response += chunk

            yield (
                json.dumps(
                    {
                        "type":
                            "delta",

                        "content":
                            chunk,
                    }
                )
                + "\n"
            )


        if replace_message_id:

            await replace_assistant_message(
                replace_message_id,
                conversation_id,
                full_response,
            )

        else:

            await save_assistant_message(
                conversation_id,
                full_response,
            )


        yield (
            json.dumps(
                {
                    "type":
                        "done"
                }
            )
            + "\n"
        )


    except asyncio.CancelledError:

        # Browser clicked Stop.
        # Closing the HTTP stream also stops
        # the upstream Ollama stream.

        print(
            "Generation stopped by user."
        )

        raise


    except Exception as error:

        print(
            "Streaming error:",
            error
        )

        yield (
            json.dumps(
                {
                    "type":
                        "error",

                    "message":
                        str(error),
                }
            )
            + "\n"
        )


@router.post(
    "/chat/stream",
)
async def chat_stream(
    request: ChatRequest,
):

    try:

        (
            conversation_id,
            history,
        ) = await prepare_chat(
            conversation_id=
                request.conversation_id,

            message=
                request.message,
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    return StreamingResponse(
        create_stream(
            conversation_id,
            history,
        ),

        media_type=
            "application/x-ndjson",

        headers={
            "Cache-Control":
                "no-cache",

            "X-Accel-Buffering":
                "no",
        },
    )


@router.post(
    "/chat/regenerate/stream",
)
async def regenerate_stream(
    request: RegenerateRequest,
):

    try:

        (
            conversation_id,
            history,
            assistant_message_id,
        ) = await prepare_regeneration(
            request.conversation_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    return StreamingResponse(
        create_stream(
            conversation_id,
            history,

            replace_message_id=
                assistant_message_id,
        ),

        media_type=
            "application/x-ndjson",

        headers={
            "Cache-Control":
                "no-cache",

            "X-Accel-Buffering":
                "no",
        },
    )