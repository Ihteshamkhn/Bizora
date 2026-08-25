from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    APP_NAME: str = "Bizora AI Business Manager"
    DEBUG: bool = True

    # Database (SQLite by default for zero-setup local dev;
    # set DATABASE_URL in .env to postgresql+psycopg2://... in production)
    DATABASE_URL: str = "sqlite:///./bizora.db"

    # Auth
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # LLM (Groq — OpenAI-compatible)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 50

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
