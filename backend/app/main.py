from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import check_mongodb_connection
from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router


app = FastAPI(
    title="Chatbot AI API",
    version="1.0.0",
    description="Professional conversational AI chatbot backend.",
)


# -----------------------------
# CORS Configuration
# -----------------------------

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# API Routes
# -----------------------------

app.include_router(chat_router)
app.include_router(conversations_router)


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