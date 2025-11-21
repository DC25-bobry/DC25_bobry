from __future__ import annotations

import io
import json
import logging
import uuid
from typing import List, Optional

from googleapiclient.discovery import Resource
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from pydantic import BaseModel, ValidationError

from backend.src.models.candidate_matching import JobMatch
from backend.src.models.candidate_profile import CandidateProfile
from backend.src.services.google_drive_connect import get_service, list_files

logger = logging.getLogger(__name__)


class CandidateRecord(BaseModel):
    id: str
    profile: CandidateProfile
    cv_drive_file_id: Optional[str] = None

    job_matches: List[JobMatch] = []
    global_rejection_reason: Optional[str] = None

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

        logger.info("Directory 'CV' does not exist. Creating a new folder on Google Drive.")
        metadata = {
            "name": self.FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder",
        }
        created = self.service.files().create(body=metadata, fields="id").execute()
        return created["id"]

    def _find_json_file(self) -> Optional[str]:
        query = (
            f"'{self.folder_id}' in parents and "
            f"trashed = false and "
            f"name = '{self.FILE_NAME}'"
        )

        result = (
            self.service.files()
            .list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime)",
            )
            .execute()
        )
        files = result.get("files", [])

        if not files:
            return None

        if len(files) == 1:
            return files[0]["id"]

        files_sorted = sorted(
            files,
            key=lambda f: f.get("modifiedTime", ""),
            reverse=True,
        )
        newest = files_sorted[0]
        to_delete = files_sorted[1:]

        for old in to_delete:
            try:
                self.service.files().delete(fileId=old["id"]).execute()
                logger.warning(
                    "Deleting duplicate candidates.json (id=%s)", old.get("id")
                )
            except Exception as e:
                logger.error(
                    "Could not delete duplicate candidates.json (id=%s): %s",
                    old.get("id"),
                    e,
                )

        return newest["id"]

    def load_all(self) -> List[CandidateRecord]:
        file_id = self._find_json_file()
        if not file_id:
            return []

        request = self.service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        buffer.seek(0)

        try:
            raw_list = json.load(io.TextIOWrapper(buffer, encoding="utf-8"))
        except json.JSONDecodeError as e:
            logger.error("Wrong JSON in candidates.json, returning empty list: %s", e)
            return []

        records: List[CandidateRecord] = []
        for item in raw_list:
            try:
                records.append(CandidateRecord(**item))
            except ValidationError as e:
                logger.error(
                    "Wrong record in candidates.json, skipping: %s", e
                )
                continue

        return records

    def save_all(self, records: List[CandidateRecord]) -> None:
        json_bytes = json.dumps(
            [r.model_dump() for r in records],
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")

        existing_file_id = self._find_json_file()
        if existing_file_id:
            try:
                self.service.files().delete(fileId=existing_file_id).execute()
            except Exception as e:
                logger.error(
                    "Could not delete old candidate from candidates.json (id=%s): %s",
                    existing_file_id,
                    e,
                )

        media = MediaIoBaseUpload(
            io.BytesIO(json_bytes),
            mimetype="application/json",
            resumable=False,
        )
        metadata = {
            "name": self.FILE_NAME,
            "parents": [self.folder_id],
        }

        self.service.files().create(
            body=metadata,
            media_body=media,
            fields="id",
        ).execute()

        logger.info("Saved %d caniddates to candidates.json", len(records))

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
            cv_drive_file_id=cv_drive_file_id,
            job_matches=job_matches or [],
            global_rejection_reason=global_rejection_reason,
        )

        records.append(new_record)
        self.save_all(records)

        return new_record

    def delete_candidate(self, candidate_id: str) -> bool:
        records = self.load_all()
        before = len(records)
        records = [r for r in records if r.id != candidate_id]
        after = len(records)

        if after == before:
            return False

        self.save_all(records)
        logger.info("Candidate %s was deleted from candidates.json", candidate_id)
        return True
