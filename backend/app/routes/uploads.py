import asyncio
import json

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from fastapi.responses import StreamingResponse

from app.services.chat_service import (
    create_conversation,
    get_conversation_history,
    save_assistant_message,
    save_user_message,
)

from app.services.vision_service import stream_vision_response


router = APIRouter(
    prefix="/api",
    tags=["Images"],
)


ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


MAX_IMAGE_SIZE = 10 * 1024 * 1024


@router.post("/chat/image/stream")
async def image_chat_stream(
    message: str = Form(...),
    conversation_id: str | None = Form(None),
    image: UploadFile = File(...),
):
    # -----------------------------
    # Validate image type
    # -----------------------------
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, PNG and WEBP "
                "images are supported."
            ),
        )

    # -----------------------------
    # Read uploaded image
    # -----------------------------
    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Image is empty.",
        )

    # -----------------------------
    # Validate image size
    # -----------------------------
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image must be smaller than 10 MB.",
        )

    # -----------------------------
    # Prepare user message
    # -----------------------------
    clean_message = message.strip()

    if not clean_message:
        clean_message = "Please describe this image."

    try:
        # Create conversation if this is a new chat
        if not conversation_id:
            conversation_id = await create_conversation(
                clean_message
            )

        # Get previous text conversation history
        history = await get_conversation_history(
            conversation_id,
            limit=18,
        )

        # Save current user question
        await save_user_message(
            conversation_id,
            clean_message,
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

    # -----------------------------
    # Streaming generator
    # -----------------------------
    async def generate():
        full_response = ""

        # First send conversation metadata
        yield (
            json.dumps(
                {
                    "type": "meta",
                    "conversation_id": conversation_id,
                    "image_name": image.filename,
                }
            )
            + "\n"
        )

        try:
            async for chunk in stream_vision_response(
                prompt=clean_message,
                image_bytes=image_bytes,
                history=history,
            ):
                full_response += chunk

                yield (
                    json.dumps(
                        {
                            "type": "delta",
                            "content": chunk,
                        }
                    )
                    + "\n"
                )

            # Save completed AI response
            await save_assistant_message(
                conversation_id,
                full_response,
            )

            yield (
                json.dumps(
                    {
                        "type": "done",
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
                        "type": "error",
                        "message": str(error),
                    }
                )
                + "\n"
            )

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )