import certifi

from pymongo import AsyncMongoClient

from app.config import settings


client = AsyncMongoClient(
    settings.MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
)


database = client[settings.MONGO_DB_NAME]


conversations_collection = database["conversations"]

messages_collection = database["messages"]


async def check_mongodb_connection():
    try:
        await client.admin.command("ping")

        print("MongoDB connected successfully")

        return True

    except Exception as error:

        print("\nMongoDB connection failed:")
        print(error)

        return False