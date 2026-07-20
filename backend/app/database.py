"""
database.py
------------
Handles the async MongoDB connection using Motor.

We keep ONE client for the whole app's lifetime (created on startup,
closed on shutdown) instead of opening a new connection per request,
which is what makes this scale well under load.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "chatbot_db")

client: AsyncIOMotorClient | None = None
db = None


async def connect_to_mongo():
    """Called once when the FastAPI app starts up."""
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Helpful indexes: fast lookup of a conversation's messages in order,
    # and fast listing of conversations by most-recently-updated.
    await db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
    await db.conversations.create_index([("updated_at", -1)])

    print(f"Connected to MongoDB at {MONGO_URI}, database '{DB_NAME}'")


async def close_mongo_connection():
    """Called once when the FastAPI app shuts down."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


def get_db():
    """Dependency-style accessor used by route handlers."""
    return db
