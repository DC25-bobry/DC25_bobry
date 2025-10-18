from __future__ import annotations
import io
import os
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Full drive scope (change to readonly if you only need read access)
SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_service(scopes: List[str] = SCOPES):
        """Authenticate and return an authorized Drive v3 service using refresh token."""
        # Get credentials from environment variables
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
        
        if not client_id or not client_secret or not refresh_token:
                raise ValueError("GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REFRESH_TOKEN must be set in .env file")
        
        # Validate that credentials are not placeholder values
        if client_id == "your_client_id_here" or client_secret == "your_client_secret_here" or refresh_token == "your_refresh_token_here":
                raise ValueError("Please replace placeholder values in .env file with actual Google API credentials")
        
        # Create credentials object directly from refresh token
        creds = Credentials(
                token=None,  # Access token will be obtained automatically
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes
        )
        
        # Refresh the token to get a valid access token
        try:
                creds.refresh(Request())
        except Exception as e:
                error_msg = str(e)
                if "unauthorized_client" in error_msg.lower():
                        raise ValueError(
                                f"OAuth client unauthorized. This usually means:\n"
                                f"1. Invalid client_id or client_secret\n"
                                f"2. OAuth consent screen not configured properly\n"
                                f"3. Application type mismatch in Google Cloud Console\n"
                                f"Original error: {error_msg}"
                        )
                elif "invalid_grant" in error_msg.lower():
                        raise ValueError(
                                f"Invalid refresh token. This usually means:\n"
                                f"1. Refresh token has expired (generate a new one)\n"
                                f"2. Refresh token was revoked\n"
                                f"3. Scopes have changed\n"
                                f"Please run get_refresh_token.py to generate a new token.\n"
                                f"Original error: {error_msg}"
                        )
                else:
                        raise ValueError(f"Failed to refresh token: {error_msg}")

        service = build("drive", "v3", credentials=creds)
        return service


def list_files(service, page_size: int = 10) -> List[Dict]:
        """List files in the authenticated user's Drive. Returns list of file metadata dicts."""
        results = service.files().list(
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
        ).execute()
        return results.get("files", [])


def upload_file(service, file_path: str, mime_type: Optional[str] = None, parent_folder_id: Optional[str] = None, file_name: Optional[str] = None) -> Dict:
        """Upload a local file. Returns the created file resource metadata."""
        name = file_name if file_name else os.path.basename(file_path)
        metadata = {"name": name}
        if parent_folder_id:
                metadata["parents"] = [parent_folder_id]
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        created = service.files().create(body=metadata, media_body=media, fields="id, name, mimeType").execute()
        return created


def download_file(service, file_id: str, dest_path: str):
        """Download a file by file_id to dest_path."""
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(dest_path, mode="wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
                status, done = downloader.next_chunk()
        fh.close()


def delete_file(service, file_id: str) -> bool:
        """Delete a file by file_id. Returns True if successful."""
        try:
                service.files().delete(fileId=file_id).execute()
                return True
        except Exception as e:
                raise e


if __name__ == "__main__":
        svc = get_service()
        print("Listing first 10 files:")
        for f in list_files(svc, page_size=10):
                print(f"{f.get('name')} ({f.get('id')}) - {f.get('mimeType')}")