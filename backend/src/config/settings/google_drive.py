from .base import BaseSettingsConfig, SettingsConfigDict


class GoogleDriveSettings(BaseSettingsConfig):
    GOOGLE_DRIVE_CLIENT_ID: str
    GOOGLE_DRIVE_CLIENT_SECRET: str
    GOOGLE_DRIVE_DIR_ID: str
    GOOGLE_REFRESH_TOKEN: str
    GOOGLE_KEY: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
