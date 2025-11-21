from __future__ import annotations

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.src.config.loader import Config
from backend.src.config.settings.smtp import SMTPSettings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(template_name: str, **context: Any) -> str:
    template = _env.get_template(template_name)
    return template.render(**context)


def send_email(to_address: str, subject: str, html_body: str) -> None:
    config = Config()
    smtp_settings: SMTPSettings = config.smtp
    host = smtp_settings.SMTP_HOST
    port = smtp_settings.SMTP_PORT
    encryption = smtp_settings.SMTP_ENCRYPTION
    user = smtp_settings.SMTP_USER
    password = smtp_settings.SMTP_PASSWORD
    email = smtp_settings.SMTP_EMAIL

    if not password:
        logger.error(
            "SMTP password is not configured",
            extra={"event": "smtp_missing_password"},
        )
        raise RuntimeError("SMTP password is not configured")

    msg = MIMEMultipart("alternative")
    msg["From"] = email
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    logger.info(
        "Sending email",
        extra={
            "event": "smtp_send_email",
            "to": to_address,
            "subject": subject,
            "host": host,
            "port": port,
            "encryption": encryption,
        },
    )

    if encryption == "ssl":
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            server.login(user, password)
            server.send_message(msg)
