import asyncio
import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from fastapi.responses import (
    StreamingResponse,
)

from app.services.auth_service import (
    get_current_user,
)

from app.services.chat_service import (
    create_conversation,
    get_conversation_history,
    save_assistant_message,
    save_user_message,
    verify_conversation_owner,
)

from app.services.vision_service import (
    stream_vision_response,
)


router = APIRouter(
    prefix="/api",
    tags=["Images"],
)


ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


MAX_IMAGE_SIZE = (
    10 * 1024 * 1024
)


@router.post(
    "/chat/image/stream"
)
async def image_chat_stream(
    message: str = Form(...),

    conversation_id:
        str | None =
        Form(None),

    image: UploadFile =
        File(...),

    current_user=
        Depends(
            get_current_user
        ),
):
    user_id = (
        current_user["user_id"]
    )

    if (
        image.content_type
        not in ALLOWED_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, PNG "
                "and WEBP images are supported."
            ),
        )

    image_bytes = (
        await image.read()
    )

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail=
                "Image is empty.",
        )

    if (
        len(image_bytes)
        > MAX_IMAGE_SIZE
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Image must be smaller "
                "than 10 MB."
            ),
        )

    clean_message = (
        message.strip()
    )

    if not clean_message:
        clean_message = (
            "Please describe this image."
        )

    try:
        if not conversation_id:
            conversation_id = (
                await create_conversation(
                    clean_message,
                    user_id,
                )
            )

        else:
            await verify_conversation_owner(
                conversation_id,
                user_id,
            )

        history = (
            await get_conversation_history(
                conversation_id,
                limit=18,
            )
        )

        await save_user_message(
            conversation_id,
            clean_message,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:
        print(
            "Image chat preparation error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    async def generate():
        full_response = ""

        yield (
            json.dumps(
                {
                    "type":
                        "meta",

                    "conversation_id":
                        conversation_id,

                    "image_name":
                        image.filename,
                }
            )
            + "\n"
        )

        try:
            async for chunk in (
                stream_vision_response(
                    prompt=
                        clean_message,

                    image_bytes=
                        image_bytes,

                    history=
                        history,
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
                        "type":
                            "done"
                    }
                )
                + "\n"
            )

        except asyncio.CancelledError:
            print(
                "Image generation stopped by user."
            )

            raise

        except Exception as error:
            print(
                "Vision streaming error:",
                error,
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

    return StreamingResponse(
        generate(),

        media_type=
            "application/x-ndjson",

        headers={
            "Cache-Control":
                "no-cache",

            "X-Accel-Buffering":
                "no",
        },
    )