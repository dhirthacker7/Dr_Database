from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Internal DB (stores reports & config)
    APP_DB_URL: str = "sqlite:///./dr_database_internal.db"

    # LLM provider
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str

    # App metadata
    APP_ENV: str = "local"
    APP_NAME: str = "Dr. Database"

    class Config:
        env_file = ".env"


settings = Settings()
# Access settings via `from app.core.settings import settings`