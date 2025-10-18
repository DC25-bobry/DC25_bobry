#!/usr/bin/env python3
"""
Utility script to obtain a Google OAuth2 refresh token.
Run this script once to get your refresh token, then add it to your .env file.
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_refresh_token():
    """Get a refresh token using OAuth2 flow."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Error: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env file")
        return None
    
    # Validate that credentials are not placeholder values
    if client_id == "your_client_id_here" or client_secret == "your_client_secret_here":
        print("Error: Please replace placeholder values in .env file with actual Google API credentials")
        return None
    
    print(f"Using client ID: {client_id[:20]}...")
    
    # Create client config
    client_config = {
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
        # Run OAuth flow with fixed port
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=8080, open_browser=True)
        
        return creds.refresh_token
    except Exception as e:
        print(f"Error during OAuth flow: {str(e)}")
        return None

if __name__ == "__main__":
    print("Getting refresh token...")
    print("Make sure you have GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET set in your .env file")
    print()
    
    refresh_token = get_refresh_token()
    
    if refresh_token:
        print(f"Success! Your refresh token is:")
        print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
        print()
        print("Add this to your .env file and you're ready to go!")
    else:
        print("Failed to get refresh token. Please check your credentials.")
