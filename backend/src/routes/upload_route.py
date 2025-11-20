import threading
import logging
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse

from backend.src.models.job_offers_model import JobOffer
from backend.src.routes.job_offers_route import get_repo
from backend.src.services.cv_storage import save_cv_file_to_drive
from backend.src.services.job_offers.job_offers_repository import JobOfferRepository
from backend.src.utils.file_validation import validate_file
from backend.src.services.document_parsing import DocumentParsingService
from backend.src.services.cv_processing import process_file


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_class=HTMLResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    job_repo: JobOfferRepository = Depends(get_repo),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files sent")

    jobs: List[JobOffer] = await job_repo.list()

    parsing_service = DocumentParsingService()
    error_count = 0
    wrong_files = ""

    for file in files:
        file_bytes = await file.read()

        file_valid, _ = validate_file(file_bytes, file.filename, file.content_type)
        if not file_valid:
            error_count += 1
            wrong_files += file.filename + " "
            continue

        try:
            drive_file_id = save_cv_file_to_drive(
                file_bytes=file_bytes,
                filename=file.filename,
                content_type=file.content_type,
            )
            logger.info(
                "CV %s zapisane w Google Drive jako id=%s",
                file.filename,
                drive_file_id,
            )
        except Exception as e:
            logger.exception("Błąd podczas zapisu CV do Google Drive: %s", e)
            error_count += 1
            wrong_files += file.filename + " "
            continue

        thread = threading.Thread(
            target=process_file,
            args=(
                file_bytes,
                file.filename,
                file.content_type,
                parsing_service,
                drive_file_id,
                jobs,
            ),
            daemon=True,
        )
        thread.start()

    processed_count = len(files) - error_count
    response_content = f"Parsing {processed_count} files."
    if error_count > 0:
        response_content += f"\nSkipped files: {wrong_files}"

    return HTMLResponse(content=response_content)
