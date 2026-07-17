"""
main.py
-------
FastAPI entrypoint.

Endpoints:
    POST   /api/chat
    GET    /api/conversations
    GET    /api/conversations/{id}
    DELETE /api/conversations/{id}

Run:
    uvicorn backend.main:app --reload --port 8000
"""

import os
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    ConversationDetail,
    MessageOut,
)

from .chat_service import (
    generate_reply,
    make_title_from_message,
    now_utc,
)

from .database import (
    connect_to_mongo,
    close_mongo_connection,
    get_db,
)


# Load environment variables from .env
load_dotenv()


# -----------------------------
# Application Lifespan
# -----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Connect to MongoDB when the application starts
    and close the connection when the application stops.
    """

    await connect_to_mongo()

    yield

    await close_mongo_connection()


# -----------------------------
# FastAPI Application
# -----------------------------

app = FastAPI(
    title="AI Chatbot API",
    description="Backend API for an AI chatbot",
    version="1.0.0",
    lifespan=lifespan,
)


# -----------------------------
# CORS Configuration
# -----------------------------

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:3000"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Health Check
# -----------------------------

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "message": "AI Chatbot API is running"
    }


# -----------------------------
# Chat Endpoint
# -----------------------------

@app.post(
    "/api/chat",
    response_model=ChatResponse
)
async def chat(payload: ChatRequest):

    db = get_db()

    conversation_id = payload.conversation_id

    # -----------------------------
    # Create new conversation
    # -----------------------------

    if conversation_id is None:

        conversation_id = str(uuid.uuid4())

        current_time = now_utc()

        await db.conversations.insert_one(
            {
                "_id": conversation_id,
                "title": make_title_from_message(
                    payload.message
                ),
                "created_at": current_time,
                "updated_at": current_time,
            }
        )

    # -----------------------------
    # Check existing conversation
    # -----------------------------

    else:

        existing = await db.conversations.find_one(
            {
                "_id": conversation_id
            }
        )

        if not existing:

            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

    # -----------------------------
    # Save user message
    # -----------------------------

    await db.messages.insert_one(
        {
            "conversation_id": conversation_id,
            "role": "user",
            "content": payload.message,
            "created_at": now_utc(),
        }
    )

    # -----------------------------
    # Generate AI response
    # -----------------------------

    try:

        reply_text = await generate_reply(
            db,
            conversation_id,
            payload.message
        )

    except Exception as e:

        print(f"OpenAI error: {e}")

        raise HTTPException(
            status_code=502,
            detail="AI service is temporarily unavailable"
        )

    # -----------------------------
    # Save assistant message
    # -----------------------------

    reply_time = now_utc()

    await db.messages.insert_one(
        {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": reply_text,
            "created_at": reply_time,
        }
    )

    # -----------------------------
    # Update conversation timestamp
    # -----------------------------

    await db.conversations.update_one(
        {
            "_id": conversation_id
        },
        {
            "$set": {
                "updated_at": reply_time
            }
        }
    )

    # -----------------------------
    # Return response
    # -----------------------------

    return ChatResponse(
        conversation_id=conversation_id,
        reply=reply_text,
        created_at=reply_time
    )


# -----------------------------
# List Conversations
# -----------------------------

@app.get(
    "/api/conversations",
    response_model=list[ConversationSummary]
)
async def list_conversations():

    db = get_db()

    cursor = (
        db.conversations
        .find()
        .sort("updated_at", -1)
    )

    docs = await cursor.to_list(
        length=200
    )

    return [
        ConversationSummary(
            id=doc["_id"],
            title=doc["title"],
            updated_at=doc["updated_at"]
        )

        for doc in docs
    ]


# -----------------------------
# Get Conversation History
# -----------------------------

@app.get(
    "/api/conversations/{conversation_id}",
    response_model=ConversationDetail
)
async def get_conversation(
    conversation_id: str
):

    db = get_db()

    # Find conversation
    conversation = await db.conversations.find_one(
        {
            "_id": conversation_id
        }
    )

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Get messages
    cursor = (
        db.messages
        .find(
            {
                "conversation_id": conversation_id
            }
        )
        .sort("created_at", 1)
    )

    docs = await cursor.to_list(
        length=1000
    )

    messages = [

        MessageOut(
            role=doc["role"],
            content=doc["content"],
            created_at=doc["created_at"]
        )

        for doc in docs
    ]

    return ConversationDetail(
        id=conversation["_id"],
        title=conversation["title"],
        messages=messages
    )


# -----------------------------
# Delete Conversation
# -----------------------------

@app.delete(
    "/api/conversations/{conversation_id}"
)
async def delete_conversation(
    conversation_id: str
):

    db = get_db()

    # Delete conversation
    result = await db.conversations.delete_one(
        {
            "_id": conversation_id
        }
    )

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Delete messages
    await db.messages.delete_many(
        {
            "conversation_id": conversation_id
        }
    )

    return {
        "status": "deleted"
    }