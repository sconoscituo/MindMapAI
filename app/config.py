from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):
    APP_NAME: str = "MindMapAI"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./mindmapai.db"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    GEMINI_API_KEY: str = ""
    PORTONE_SECRET_KEY: str = ""
    PORTONE_IMP_KEY: str = ""

    FREE_DAILY_LIMIT: int = 5

    class Config:
        env_file = ".env"


@lru_cache()
def get_config() -> Config:
    return Config()


config = get_config()
