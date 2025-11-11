import smtplib
import logging
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime
from backend.src.config.smtp_config import SMTPConfig
from backend.src.email.email_generator import EmailGenerator


class EmailService:
    def __init__(self):
        self.host = SMTPConfig.HOST
        self.port = SMTPConfig.PORT
        self.user = SMTPConfig.USER
        self.password = SMTPConfig.PASSWORD
        self.email = SMTPConfig.EMAIL
        self.encryption = SMTPConfig.ENCRYPTION
        self.logger = logging.getLogger(__name__)


    def _load_message_from_file(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            self.logger.warning(f"Message file not found: {file_path}")
            return None
        return path.read_text(encoding="utf-8")

    def send_email_from_file(self, recipient: str, subject: str, message_file: str):
        body = self._load_message_from_file(message_file)
        if body is None:
            return
        self.send_message(recipient, subject, body)

    def send_email(self, recipient: str, subject: str, message: str):
        self.send_message(recipient, subject, message)

    def send_message(self, recipient: str, subject: str, message: str):
        msg = MIMEText(message, "html", "utf-8")
        msg["From"] = self.email
        msg["To"] = recipient
        msg["Subject"] = subject

        try:
            self.logger.info(f"📨 Sending message to {recipient}...")
            with smtplib.SMTP(self.host, self.port) as server:
                if self.encryption == "tls":
                    server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            self.logger.info(f"✅  Email successfully sent to {recipient}!")
        except Exception as e:
            self.logger.error(f"❌ ERROR - failed to send email to  {recipient}: {e}")