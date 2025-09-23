"""Application configuration utilities."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = Field(default="JMD Planning API", alias="BACKEND_APP_NAME")
    environment: str = Field(default="development", alias="BACKEND_ENV")
    api_prefix: str = Field(default="/api/v1", alias="BACKEND_API_PREFIX")
    database_url: str = Field(
        default="sqlite+pysqlite:///./planning.db", alias="BACKEND_DATABASE_URL"
    )
    sqlalchemy_echo: bool = Field(default=False, alias="BACKEND_SQLALCHEMY_ECHO")
    notification_email_sender: str = Field(
        default="notifications@example.com",
        alias="BACKEND_NOTIFICATION_EMAIL_SENDER",
    )
    notification_email_recipients: list[str] = Field(
        default_factory=lambda: ["planning-team@example.com"],
        alias="BACKEND_NOTIFICATION_EMAIL_RECIPIENTS",
    )
    notification_telegram_bot_token: str = Field(
        default="demo-telegram-token",
        alias="BACKEND_NOTIFICATION_TELEGRAM_BOT_TOKEN",
    )
    notification_telegram_chat_ids: list[str] = Field(
        default_factory=lambda: ["demo-chat-id"],
        alias="BACKEND_NOTIFICATION_TELEGRAM_CHAT_IDS",
    )
    notification_email_provider: str = Field(
        default="smtp",
        alias="BACKEND_NOTIFICATION_EMAIL_PROVIDER",
    )
    notification_email_smtp_host: str = Field(
        default="localhost",
        alias="BACKEND_NOTIFICATION_EMAIL_SMTP_HOST",
    )
    notification_email_smtp_port: int = Field(
        default=1025,
        alias="BACKEND_NOTIFICATION_EMAIL_SMTP_PORT",
    )
    notification_email_api_key: str | None = Field(
        default=None,
        alias="BACKEND_NOTIFICATION_EMAIL_API_KEY",
    )
    calendar_name: str = Field(
        default="JMD Planning",
        alias="BACKEND_CALENDAR_NAME",
    )
    calendar_connectors: list[str] = Field(
        default_factory=lambda: ["google", "outlook"],
        alias="BACKEND_CALENDAR_CONNECTORS",
    )
    calendar_webhook_secret: str = Field(
        default="demo-calendar-secret",
        alias="BACKEND_CALENDAR_WEBHOOK_SECRET",
    )
    calendar_google_webhook_token: str = Field(
        default="demo-google-token",
        alias="BACKEND_CALENDAR_GOOGLE_WEBHOOK_TOKEN",
    )
    calendar_outlook_webhook_token: str = Field(
        default="demo-outlook-token",
        alias="BACKEND_CALENDAR_OUTLOOK_WEBHOOK_TOKEN",
    )
    storage_connectors: list[str] = Field(
        default_factory=lambda: ["memory"],
        alias="BACKEND_STORAGE_CONNECTORS",
    )
    storage_default_bucket: str | None = Field(
        default=None,
        alias="BACKEND_STORAGE_BUCKET",
    )
    storage_google_drive_folder: str | None = Field(
        default=None,
        alias="BACKEND_STORAGE_GOOGLE_DRIVE_FOLDER",
    )
    storage_sharepoint_site: str | None = Field(
        default=None,
        alias="BACKEND_STORAGE_SHAREPOINT_SITE",
    )
    storage_sharepoint_library: str | None = Field(
        default=None,
        alias="BACKEND_STORAGE_SHAREPOINT_LIBRARY",
    )
    storage_s3_bucket: str | None = Field(
        default=None,
        alias="BACKEND_STORAGE_S3_BUCKET",
    )
    storage_s3_region: str | None = Field(
        default=None,
        alias="BACKEND_STORAGE_S3_REGION",
    )
    audit_signature_secret: str = Field(
        default="audit-secret-demo",
        alias="BACKEND_AUDIT_SIGNATURE_SECRET",
    )
    audit_default_organization: str = Field(
        default="default-org",
        alias="BACKEND_AUDIT_DEFAULT_ORG",
    )
    audit_retention_days: int = Field(
        default=365,
        alias="BACKEND_AUDIT_RETENTION_DAYS",
    )
    audit_archive_days: int = Field(
        default=180,
        alias="BACKEND_AUDIT_ARCHIVE_DAYS",
    )
    audit_rgpd_sla_days: int = Field(
        default=30,
        alias="BACKEND_AUDIT_RGPD_SLA_DAYS",
    )

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}

    @field_validator(
        "notification_email_recipients",
        "notification_telegram_chat_ids",
        "calendar_connectors",
        "storage_connectors",
        mode="before",
    )
    @classmethod
    def _split_comma_separated(cls, value: object) -> object:
        """Allow providing list settings as comma separated strings."""

        if isinstance(value, str):
            items = [item.strip() for item in value.split(",") if item.strip()]
            return items
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
