import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file's directory so the path is correct
# regardless of which working directory the FastAPI process is launched from.
_ENV_FILE = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # --- Database ---
    # Default to local SQLite fallback if DATABASE_URL is not set in backend/.env,
    # enabling seamless offline testing and local prototype execution.
    DATABASE_URL: str = "sqlite:///./areca_agent.db"

    # Individual POSTGRES_* fields kept for local Docker-Compose dev only.
    # They are NOT used by session.py — DATABASE_URL is the single source of truth.
    POSTGRES_USER: str = "areca_user"
    POSTGRES_PASSWORD: str = "areca_pass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "areca_agent_db"

    # --- External APIs ---
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_DAILY_BUDGET_CAP: int = 100
    DATA_GOV_IN_API_KEY: str = ""

    # --- Vision Agent Backend ---
    VISION_BACKEND: str = "multicrop"  # "multicrop" | "pytorch" | "keras"
    VISION_MODEL_DIR: str = str(Path(__file__).parent / "agents" / "vision" / "weights" / "multi_crop_mobilenetv2")
    VISION_CONFIDENCE_THRESHOLD: float = 0.48
    MAX_UPLOAD_IMAGE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

