from __future__ import annotations

import json
import logging
import os
import tempfile
import uuid
from typing import List, Optional, Any

from googleapiclient.discovery import Resource
from googleapiclient.http import MediaFileUpload
from pydantic import BaseModel, ValidationError

from backend.src.services.google_drive_connect import (
    get_service,
    list_files,
    upload_file,
    download_file,
)
from backend.src.models.candidate_profile import CandidateProfile

logger = logging.getLogger(__name__)


class CandidateRecord(BaseModel):
    id: str
    profile: CandidateProfile
    cv_drive_file_id: Optional[str] = None

    job_matches: Optional[list] = None
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

        logger.info("Folder 'CV' nie istnieje – tworzę nowy folder na Google Drive.")
        metadata = {
            "name": self.FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder",
        }
        created = self.service.files().create(body=metadata, fields="id").execute()
        return created["id"]

    def _list_json_files(self) -> List[dict[str, Any]]:
        query = (
            f"'{self.folder_id}' in parents "
            f"and name='{self.FILE_NAME}' "
            f"and mimeType='application/json' "
            f"and trashed=false"
        )
        resp = (
            self.service.files()
            .list(q=query, fields="files(id, name, mimeType)")
            .execute()
        )
        return resp.get("files", [])

    def _find_json_file(self) -> Optional[str]:
        files = self._list_json_files()
        if not files:
            return None

        if len(files) > 1:
            logger.warning(
                "Znaleziono %d kopii %s w folderze '%s'. "
                "Zostawiam pierwszą (id=%s) – duplikaty zostaną usunięte przy zapisie.",
                len(files),
                self.FILE_NAME,
                self.FOLDER_NAME,
                files[0]["id"],
            )
        return files[0]["id"]

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
                        "Błędny rekord kandydata w candidates.json, pomijam: %s",
                        e,
                    )
                    continue
            return records

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def save_all(self, records: List[CandidateRecord]) -> None:
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
            json.dump([r.dict() for r in records], tmp, ensure_ascii=False, indent=2)

        try:
            existing_files = self._list_json_files()

            if existing_files:
                primary_id = existing_files[0]["id"]
                media = MediaFileUpload(
                    tmp_path,
                    mimetype="application/json",
                    resumable=False,
                )
                self.service.files().update(
                    fileId=primary_id,
                    media_body=media,
                ).execute()

                for extra in existing_files[1:]:
                    extra_id = extra.get("id")
                    try:
                        self.service.files().delete(fileId=extra_id).execute()
                        logger.info(
                            "Usunięto duplikat %s (id=%s) z folderu '%s'.",
                            self.FILE_NAME,
                            extra_id,
                            self.FOLDER_NAME,
                        )
                    except Exception as e:
                        logger.warning(
                            "Nie udało się usunąć duplikatu %s (id=%s): %s",
                            self.FILE_NAME,
                            extra_id,
                            e,
                        )

            else:
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
        cv_drive_file_id: Optional[str] = None,
        job_matches: Optional[list] = None,
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

        remaining = [r for r in records if r.id != candidate_id]

        if len(remaining) == before:
            logger.warning(
                "Próba usunięcia kandydata %s, ale nie znaleziono go w candidates.json",
                candidate_id,
            )
            return False

        self.save_all(remaining)
        logger.info(
            "Usunięto kandydata %s z candidates.json (pozostało %d rekordów)",
            candidate_id,
            len(remaining),
        )
        return True
