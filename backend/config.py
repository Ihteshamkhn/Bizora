from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    APP_NAME: str = "Bizora AI Business Manager"
    DEBUG: bool = False

    # Database defaults; in production, set DATABASE_URL to a managed PostgreSQL URL.
    DATABASE_URL: str = "sqlite:///./bizora.db"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://localhost:3000"

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

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
