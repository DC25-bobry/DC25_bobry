from __future__ import annotations

import json
import logging
import os
import tempfile
import uuid
from typing import List, Optional

from googleapiclient.discovery import Resource
from pydantic import BaseModel, ValidationError

from backend.src.services.google_drive_connect import (
    get_service,
    list_files,
    upload_file,
    download_file,
)
from backend.src.models.candidate_profile import CandidateProfile
from backend.src.models.candidate_matching import JobMatch

logger = logging.getLogger(__name__)


class CandidateRecord(BaseModel):
    id: str
    profile: CandidateProfile
    job_matches: List[JobMatch] = []
    global_rejection_reason: Optional[str] = None
    cv_drive_file_id: Optional[str] = None

    class Config:
        extra = "forbid"


class GoogleDriveCandidateStore:
    FOLDER_NAME = "CV"
    FILE_NAME = "candidates.json"

    def __init__(self) -> None:
        self.service: Resource = get_service()
        self.folder_id: str = self._ensure_cv_folder()

    def _ensure_cv_folder(self) -> str:
        files = list_files(self.service, page_size=100)

        for f in files:
            if (
                f.get("name") == self.FOLDER_NAME
                and f.get("mimeType") == "application/vnd.google-apps.folder"
            ):
                return f["id"]

        logger.info("Folder 'CV' nie istnieje – tworzę nowy folder na Google Drive.")
        metadata = {
            "name": self.FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder",
        }
        created = self.service.files().create(body=metadata, fields="id").execute()
        return created["id"]

    def _find_json_file(self) -> Optional[str]:
        query = f"'{self.folder_id}' in parents"
        files = (
            self.service.files()
            .list(q=query, fields="files(id, name, mimeType)")
            .execute()
            .get("files", [])
        )

        for f in files:
            if f.get("name") == self.FILE_NAME:
                return f["id"]

        return None

    def load_all(self) -> List[CandidateRecord]:
        file_id = self._find_json_file()
        if not file_id:
            return []

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            download_file(self.service, file_id, tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                raw_list = json.load(f)

            records: List[CandidateRecord] = []
            for item in raw_list:
                try:
                    records.append(CandidateRecord(**item))
                except ValidationError as e:
                    logger.error(
                        "Błędny rekord kandydata w candidates.json, pomijam: %s", e
                    )
                    continue
            return records

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def save_all(self, records: List[CandidateRecord]) -> None:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as tmp:
            tmp_path = tmp.name
            json.dump(
                [r.model_dump() for r in records],
                tmp,
                ensure_ascii=False,
                indent=2,
            )

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

            logger.info("Zapisano %d kandydatów do candidates.json", len(records))

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def append_candidate(
        self,
        profile: CandidateProfile,
        job_matches: Optional[List[JobMatch]] = None,
        cv_drive_file_id: Optional[str] = None,
        global_rejection_reason: Optional[str] = None,
    ) -> CandidateRecord:
        records = self.load_all()

        new_record = CandidateRecord(
            id=str(uuid.uuid4()),
            profile=profile,
            job_matches=job_matches or [],
            global_rejection_reason=global_rejection_reason,
            cv_drive_file_id=cv_drive_file_id,
        )

        records.append(new_record)
        self.save_all(records)

        return new_record
