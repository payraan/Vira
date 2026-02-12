from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vira"
    environment: str = "local"

    # Database
    database_url: str = "postgresql+asyncpg://vira:vira@localhost:5432/vira"

    # Telegram
    telegram_bot_token: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
