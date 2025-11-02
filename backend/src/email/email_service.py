import smtplib
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime
from backend.src.config.smtp_config import SMTPConfig

class EmailService:
    def __init__(self):
        self.host = SMTPConfig.HOST
        self.port = SMTPConfig.PORT
        self.user = SMTPConfig.USER
        self.password = SMTPConfig.PASSWORD
        self.email = SMTPConfig.EMAIL
        self.encryption = SMTPConfig.ENCRYPTION
        
        self.log_dir = Path("backend/logs/email_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = self.log_dir / f"email_log_{timestamp}.txt"

       #  self._write_log(f"📧 Sesja rozpoczęta: {timestamp}")

    def _write_log(self, message: str):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time}] {message}\n")

    def _load_message_from_file(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            warning = f"Nie znaleziono pliku wiadomości: {file_path} — pominięto wysyłkę."
            print(warning)
            self._write_log(warning)
            return None
        return path.read_text(encoding="utf-8")

    def send_email(self, recipient: str, subject: str, message_file: str):
        """Wysyła wiadomość e-mail i loguje wynik."""
        body = self._load_message_from_file(message_file)
        if body is None:
            return  # brak pliku, nie wysyłamy

        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = self.email
        msg["To"] = recipient
        msg["Subject"] = subject

        try:
            print(f"📨 Wysyłanie wiadomości do {recipient}...")
            with smtplib.SMTP(self.host, self.port) as server:
                if self.encryption == "tls":
                    server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            print(f"✅ Wiadomość wysłana pomyślnie do {recipient}!")
            self._write_log(f"✅ Sukces: Wiadomość wysłana do {recipient}")
        except Exception as e:
            error_msg = f"❌ Błąd podczas wysyłania do {recipient}: {e}"
            print(error_msg)
            self._write_log(error_msg)