from .base import BaseSettingsConfig, SettingsConfigDict


class CoreSettings(BaseSettingsConfig):
    APP_NAME: str = "DC25_bobry Backend API"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
