from fastapi import APIRouter, HTTPException, Depends, status
from googleapiclient.discovery import Resource
from pydantic import BaseModel
from typing import List, Optional


from backend.src.services.google_drive_connect import (
    get_service, list_files, upload_file, download_file, delete_file
)

router = APIRouter(prefix="/drive", tags=["Google Drive"])


class DriveFile(BaseModel):
    id: str
    name: str
    mime_type: str
    size: Optional[str] = None
    modified_time: Optional[str] = None


class FileListResponse(BaseModel):
    files: List[DriveFile]
    count: int


class UploadResponse(BaseModel):
    id: str
    name: str
    mime_type: str
    message: str


class DeleteResponse(BaseModel):
    message: str
    file_id: str


def get_drive_service() -> Resource:
    try:
        return get_service()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to Google Drive: {str(e)}"
        )


@router.get("/files", response_model=FileListResponse)
async def list_drive_files(page_size: int = 10, service=Depends(get_drive_service)):
    files_data = list_files(service, page_size)
    files = [
        DriveFile(
            id=f["id"], name=f["name"], mime_type=f["mimeType"],
            size=f.get("size"), modified_time=f.get("modifiedTime")
        )
        for f in files_data
    ]
    return FileListResponse(files=files, count=len(files))
