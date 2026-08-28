from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    # =========================================
    # MongoDB
    # =========================================

    MONGO_URI: str

    MONGO_DB_NAME: str = (
        "chatbot_ai"
    )


    # =========================================
    # AI Provider
    # =========================================

    # ollama = local development
    # gemini = production deployment
    AI_PROVIDER: str = "ollama"


    # =========================================
    # Ollama
    # =========================================

    OLLAMA_BASE_URL: str = (
        "http://localhost:11434"
    )

    OLLAMA_MODEL: str = (
        "llama3.2:3b"
    )

    OLLAMA_VISION_MODEL: str = (
        "gemma3:4b"
    )


    # =========================================
    # Gemini
    # =========================================

    GEMINI_API_KEY: str | None = None

    GEMINI_MODEL: str = (
        "gemini-3.7-flash"
    )

    GEMINI_VISION_MODEL: str = (
        "gemini-3.7-flash"
    )


    # =========================================
    # Authentication
    # =========================================

    JWT_SECRET: str

    JWT_ALGORITHM: str = (
        "HS256"
    )

    JWT_EXPIRE_MINUTES: int = (
        10080
    )


    # =========================================
    # Frontend
    # =========================================

    FRONTEND_URL: str = (
        "http://localhost:5173"
    )


    # =========================================
    # Optional PostgreSQL
    # =========================================

    DATABASE_URL: str | None = None


    model_config = (
        SettingsConfigDict(
            env_file=".env",
            extra="ignore",
        )
    )


settings = Settings()