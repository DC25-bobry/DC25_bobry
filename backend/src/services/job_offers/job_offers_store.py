import json
import logging
import os
import tempfile
from typing import List, Dict, Any, Optional

from fastapi import HTTPException
from googleapiclient.discovery import Resource

from backend.src.services.google_drive_connect import (
    get_service,
    list_files,
    upload_file,
    download_file,
)

logger = logging.getLogger(__name__)


class GoogleDriveJobOfferStore:
    FOLDER_NAME = "oferta"
    FILE_NAME = "job_offers.json"

    def __init__(self):
        self.service: Optional[Resource] = None
        self.folder_id: Optional[str] = None

    def _ensure_service(self):
        if self.service is None:
            self.service = get_service()

    def _find_folder(self) -> Optional[str]:
        self._ensure_service()
        files = list_files(self.service, page_size=100)

        for f in files:
            if f.get("name") == self.FOLDER_NAME and \
                    f.get("mimeType") == "application/vnd.google-apps.folder":
                return f["id"]

        return None

    def _create_folder(self) -> str:
        self._ensure_service()
        file_metadata = {
            "name": self.FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder"
        }

        created = self.service.files().create(
            body=file_metadata,
            fields="id"
        ).execute()

        return created["id"]

    def _ensure_folder(self):
        if self.folder_id:
            return

        folder = self._find_folder()
        if folder:
            self.folder_id = folder
        else:
            logger.info("Directory 'oferta' does not exist. Creating a new folder on Google Drive.")
            self.folder_id = self._create_folder()

    def _find_json_file(self) -> Optional[str]:
        self._ensure_service()
        self._ensure_folder()

        query = f"'{self.folder_id}' in parents"
        files = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType)"
        ).execute().get("files", [])

        for f in files:
            if f["name"] == self.FILE_NAME:
                return f["id"]

        return None

    async def load_all(self) -> List[Dict[str, Any]]:
        self._ensure_service()
        self._ensure_folder()

        file_id = self._find_json_file()
        if not file_id:
            return []

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            download_file(self.service, file_id, tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception as e:
            logger.error("Error occured when reading from job_offers.json: %s", e)
            return []

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def save_all(self, offers: List[Dict[str, Any]]):
        self._ensure_service()
        self._ensure_folder()

        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as tmp:
            tmp_path = tmp.name
            json.dump(offers, tmp, ensure_ascii=False, indent=2)

        try:
            existing_file_id = self._find_json_file()

            if existing_file_id:
                self.service.files().delete(fileId=existing_file_id).execute()

            upload_file(
                service=self.service,
                file_path=tmp_path,
                mime_type="application/json",
                parent_folder_id=self.folder_id,
                file_name=self.FILE_NAME,
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Błąd zapisu job_offers.json: {e}"
            )

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
