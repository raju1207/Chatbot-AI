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
)

from app.services.chat_service import (
    prepare_chat,
    process_chat,
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

        print(
            "Stream preparation error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    async def generate():

        full_response = ""

        # First tell React which
        # conversation is being used.
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


            await save_assistant_message(
                conversation_id,
                full_response,
            )


            yield (
                json.dumps(
                    {
                        "type": "done"
                    }
                )
                + "\n"
            )


        except Exception as error:

            print(
                "Streaming error:",
                error
            )

            yield (
                json.dumps(
                    {
                        "type": "error",
                        "message":
                            str(error),
                    }
                )
                + "\n"
            )


    return StreamingResponse(
        generate(),
        media_type=
            "application/x-ndjson",
    )