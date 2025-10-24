#!/usr/bin/env python3
"""
Utility script to obtain a Google OAuth2 refresh token.
Run this script once to get your refresh token, then add it to your .env file.
"""
import logging
from typing import Optional

from google_auth_oauthlib.flow import InstalledAppFlow

from backend.src.config.logging_config import configure_logging
from settings import Settings

configure_logging()

logger = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/drive"]
settings = Settings()

def get_refresh_token() -> Optional[str]:
    """Get a refresh token using OAuth2 flow."""
    client_id: Optional[str] = settings.google_drive_client_id
    client_secret: Optional[str] = settings.google_drive_client_secret

    if not client_id or not client_secret:
        logger.error("GOOGLE_DRIVE_CLIENT_ID and GOOGLE_DRIVE_CLIENT_SECRET must be set in .env file")
        return None
    
    # Validate that credentials are not placeholder values
    if client_id == "yourID.apps.googleusercontent.com" or client_secret == "yourSecret":
        logger.error("Please replace placeholder values in .env file with actual Google API credentials")
        return None
    
    logger.info(f"Using client ID: {client_id[:20]}...")
    
    # Create client config
    client_config: dict = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://blabla:8080", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    
    try:
        # Run OAuth flow with a fixed port
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=8080, open_browser=True)
        
        return creds.refresh_token
    except Exception as e:
        logger.error(f"Error during OAuth flow: {str(e)}")
        return None

if __name__ == "__main__":
    logger.info("Getting refresh token..."
                "Make sure you have GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET set in your .env file")
    
    refresh_token: Optional[str] = get_refresh_token()

    if refresh_token:
        logger.info(
            f"Success! Your refresh token is:\n"
            f"GOOGLE_DRIVE_REFRESH_TOKEN={refresh_token}\n\n"
            "Add this to your .env file and you're ready to go!"
        )
    else:
        logger.error("Failed to get refresh token. Please check your credentials.")
