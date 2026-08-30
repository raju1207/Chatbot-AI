from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import check_mongodb_connection

from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router
from app.routes.uploads import router as uploads_router


app = FastAPI(
    title="Chatbot AI API",
    version="1.0.0",
    description="Professional conversational AI chatbot backend.",
)


# =========================================
# CORS
# =========================================

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_url = (
    settings.FRONTEND_URL
    .strip()
    .rstrip("/")
)

if (
    frontend_url
    and frontend_url not in origins
):
    origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# ROUTES
# =========================================

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(uploads_router)


# =========================================
# ROOT
# =========================================

@app.get("/")
async def root():
    return {
        "message": "Chatbot AI backend is running",
        "ai_provider": settings.AI_PROVIDER,
    }


# =========================================
# VERCEL HEALTH CHECK
# =========================================

@app.get("/api/health")
async def health():

    mongodb_connected = (
        await check_mongodb_connection()
    )

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
        "ai_provider":
            settings.AI_PROVIDER,
    }