from .base import BaseSettingsConfig, SettingsConfigDict


class SMTPSettings(BaseSettingsConfig):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_EMAIL: str
    SMTP_ENCRYPTION: str = "tls"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    def summary(self):
        return {
            "host": self.SMTP_HOST,
            "port": self.SMTP_PORT,
            "user": self.SMTP_USER,
            "email": self.SMTP_EMAIL,
            "encryption": self.SMTP_ENCRYPTION,
        }
