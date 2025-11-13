from __future__ import annotations
import io
import logging
import os
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from backend.src.config.logging_config import configure_logging
from backend.src.config.loader import Config

configure_logging()
logger = logging.getLogger(__name__)

SCOPES: List[str] = ["https://www.googleapis.com/auth/drive"]
config = Config()


def get_service(scopes=None) -> Resource:
    if scopes is None:
        scopes = SCOPES
    gd = config.google_drive

    if not all([gd.google_drive_client_id, gd.google_drive_client_secret, gd.google_refresh_token]):
        raise ValueError("Google Drive credentials not found in .env")

    creds: Credentials = Credentials(
        token=None,
        refresh_token=gd.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=gd.google_drive_client_id,
        client_secret=gd.google_drive_client_secret,
        scopes=scopes
    )

    try:
        creds.refresh(Request())
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google Drive service: {e}")


def list_files(service, page_size: int = 10) -> List[Dict]:
    results = service.files().list(
        pageSize=page_size,
        fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
    ).execute()
    return results.get("files", [])


def upload_file(service, file_path: str, mime_type: Optional[str] = None,
                parent_folder_id: Optional[str] = None, file_name: Optional[str] = None) -> Dict:
    metadata = {"name": file_name or os.path.basename(file_path)}
    if parent_folder_id:
        metadata["parents"] = [parent_folder_id]
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    return service.files().create(body=metadata, media_body=media,
                                  fields="id, name, mimeType").execute()


def download_file(service, file_id: str, dest_path: str) -> None:
    request = service.files().get_media(fileId=file_id)
    with io.FileIO(dest_path, mode="wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()


def delete_file(service, file_id: str) -> bool:
    service.files().delete(fileId=file_id).execute()
    return True
