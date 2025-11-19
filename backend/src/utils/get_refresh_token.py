#!/usr/bin/env python3
"""
Utility script to obtain a Google OAuth2 refresh token.
Run this script once to get your refresh token, then add it to your .env file.
"""
import logging
from typing import Optional
from google_auth_oauthlib.flow import InstalledAppFlow

from backend.src.config.logging_config import configure_logging
from backend.src.config.loader import Config

configure_logging()
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]
config = Config()


def get_refresh_token() -> Optional[str]:
    gd = config.google_drive
    cid = gd.GOOGLE_DRIVE_CLIENT_ID
    secret = gd.GOOGLE_DRIVE_CLIENT_SECRET

    if not cid or not secret:
        logger.error("Missing GOOGLE_DRIVE_CLIENT_ID or GOOGLE_DRIVE_CLIENT_SECRET in .env")
        return None

    client_config = {
        "installed": {
            "client_id": cid,
            "client_secret": secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }

    try:
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=8080)
        return creds.refresh_token
    except Exception as e:
        logger.error(f"OAuth flow failed: {e}")
        return None


if __name__ == "__main__":
    logger.info("Getting refresh token...")
    token = get_refresh_token()
    if token:
        logger.info(f"✅ Refresh token:\nGOOGLE_DRIVE_REFRESH_TOKEN={token}\n")
    else:
        logger.error("❌ Failed to retrieve refresh token.")
