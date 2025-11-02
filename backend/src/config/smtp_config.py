import os
from dotenv import load_dotenv

load_dotenv()

class SMTPConfig:
    HOST = os.getenv("SMTP_HOST")
    PORT = int(os.getenv("SMTP_PORT", 587))
    USER = os.getenv("SMTP_USER")
    PASSWORD = os.getenv("SMTP_PASSWORD")
    EMAIL = os.getenv("SMTP_EMAIL", USER)
    ENCRYPTION = os.getenv("SMTP_ENCRYPTION", "tls").lower()

    @staticmethod
    def summary():
        return {
            "host": SMTPConfig.HOST,
            "port": SMTPConfig.PORT,
            "user": SMTPConfig.USER,
            "email": SMTPConfig.EMAIL,
            "encryption": SMTPConfig.ENCRYPTION,
        }
