from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings are read from environment variables (or a local .env file)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "StockWise Inventory API"
    app_version: str = "1.0.0"
    database_url: str = "postgresql+psycopg://stockwise:stockwise@localhost:5432/stockwise"
    log_level: str = "INFO"


settings = Settings()
