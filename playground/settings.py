from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database settings
    SQLITE_DB_PATH: str = ":memory:"

    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    # AutoAgent settings
    AGENTR_API_KEY: str | None = None
    AGENTR_BASE_URL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

# Ensure data directory exists
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
