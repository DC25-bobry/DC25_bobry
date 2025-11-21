from __future__ import annotations

import logging
from typing import Optional

from backend.src.services.email.email_client import render_template, send_email

logger = logging.getLogger(__name__)


def _build_display_name(name: Optional[str]) -> str:
    if name:
        return name
    return "Kandydacie"


def send_accept_email(
    name: Optional[str],
    email: str,
    position: str,
) -> None:
    display_name = _build_display_name(name)

    html_body = render_template(
        "template_approval.html",
        name=display_name,
        position=position,
    )
    subject = f"Decyzja rekrutacyjna – {position}"

    logger.info(
        "Sending acceptance email",
        extra={
            "event": "send_accept_email",
            "email": email,
            "position": position,
        },
    )

    send_email(email, subject, html_body)


def send_reject_all_email(
    name: Optional[str],
    email: str,
) -> None:
    display_name = _build_display_name(name)

    html_body = render_template(
        "template_rejection_global.html",
        name=display_name,
    )
    subject = "Decyzja rekrutacyjna – BóbrPol"

    logger.info(
        "Sending global rejection email",
        extra={
            "event": "send_reject_all_email",
            "email": email,
        },
    )

    send_email(email, subject, html_body)

def send_reject_matched_email(
    name: Optional[str],
    email: str,
    position: str,
) -> None:
    display_name = _build_display_name(name)

    html_body = render_template(
        "template_rejection_matched.html",
        name=display_name,
        position=position
    )
    subject = "Decyzja rekrutacyjna – BóbrPol"

    logger.info(
        "Sending matched rejection email",
        extra={
            "event": "send_reject_matched_email",
            "email": email,
            "position": position,
        },
    )

    send_email(email, subject, html_body)
