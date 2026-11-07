from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Web Monitor"
    debug: bool = True
    secret_key: str = "cambia-esto"
    api_username: str = "admin"
    api_password: str = "change-me"

    # Database
    database_url: str = "postgresql+asyncpg://monitor:monitor_secret@localhost:5432/webmonitor"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""


settings = Settings()