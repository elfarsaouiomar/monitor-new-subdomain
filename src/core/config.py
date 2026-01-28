from typing import List, Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "Subdomain Monitor"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 27017
    DB_NAME: str = "subdomain_monitor"
    DB_USER: Optional[str] = None
    DB_PWD: Optional[str] = None
    COLLECTION_NAME: str = "domains"

    # DNS Resolvers
    DNS_RESOLVERS: List[str] = ["1.1.1.1", "1.0.0.1", "8.8.8.8", "8.8.4.4"]

    # Notifications
    SLACK_WEBHOOK: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Monitoring
    MONITOR_INTERVAL_MINUTES: int = 60
    MAX_WORKERS: int = 10
    DNS_TIMEOUT: int = 5

    # Scheduler
    ENABLE_SCHEDULER: bool = False
    SCHEDULER_TIMEZONE: str = "UTC"

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    @property
    def mongodb_url(self) -> str:
        """Build MongoDB connection URL"""
        if self.DB_USER and self.DB_PWD:
            return (
                f"mongodb://{self.DB_USER}:{self.DB_PWD}@{self.DB_HOST}:{self.DB_PORT}"
            )
        return f"mongodb://{self.DB_HOST}:{self.DB_PORT}"


settings = Settings()
