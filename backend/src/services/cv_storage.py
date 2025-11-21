import os
import tempfile
import logging
from typing import Optional

from googleapiclient.discovery import Resource

from backend.src.services.google_drive_connect import (
    get_service,
    list_files,
    upload_file,
)

logger = logging.getLogger(__name__)


def _ensure_cv_folder(service: Resource) -> str:
    files = list_files(service, page_size=100)

    for f in files:
        if (
            f.get("name") == "CV"
            and f.get("mimeType") == "application/vnd.google-apps.folder"
        ):
            return f["id"]

    logger.info("Folder 'CV' nie istnieje. Tworzę nowy folder na Google Drive.")
    metadata = {
        "name": "CV",
        "mimeType": "application/vnd.google-apps.folder",
    }
    created = service.files().create(body=metadata, fields="id").execute()
    return created["id"]


def save_cv_file_to_drive(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str] = None,
) -> str:
    service = get_service()
    folder_id = _ensure_cv_folder(service)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        created = upload_file(
            service=service,
            file_path=tmp_path,
            mime_type=content_type or "application/octet-stream",
            parent_folder_id=folder_id,
            file_name=filename,
        )
        file_id = created["id"]
        logger.info("Zapisano CV '%s' na Google Drive (id=%s)", filename, file_id)
        return file_id
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except PermissionError as e:
                logger.warning(
                    "Nie udało się usunąć pliku tymczasowego %s: %s",
                    tmp_path,
                    e,
                )
            except OSError as e:
                logger.warning(
                    "Błąd podczas usuwania pliku tymczasowego %s: %s",
                    tmp_path,
                    e,
                )