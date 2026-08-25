# MongoDB and PostgreSQL connections will be added here.

from pymongo import AsyncMongoClient

from app.config import settings


client = AsyncMongoClient(settings.MONGO_URI)

database = client[settings.MONGO_DB_NAME]

conversations_collection = database["conversations"]
messages_collection = database["messages"]


async def check_mongodb_connection():
    try:
        await client.admin.command("ping")
        return True

    except Exception as error:
        print(f"MongoDB connection error: {error}")
        return False