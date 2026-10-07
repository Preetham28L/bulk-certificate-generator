from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bulk Certificate Generator"
    app_version: str = "1.0.0"

    database_url: str = "sqlite:///./certificates.db"
    certificate_directory: str = "certificates"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

CERTIFICATE_DIR = Path(settings.certificate_directory)