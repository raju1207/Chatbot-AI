from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import check_mongodb_connection
from app.routes.chat import router as chat_router


app = FastAPI(
    title="Chatbot AI API",
    version="1.0.0",
    description="Professional conversational AI chatbot backend.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": "Chatbot AI backend is running"
    }


@app.get("/health")
async def health():

    mongodb_connected = await check_mongodb_connection()

    return {
        "status": (
            "healthy"
            if mongodb_connected
            else "unhealthy"
        ),
        "mongodb": (
            "connected"
            if mongodb_connected
            else "disconnected"
        ),
    }