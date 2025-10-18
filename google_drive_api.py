from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os
from google_drive_connect import get_service, list_files, upload_file, download_file, delete_file

router = APIRouter(prefix="/drive", tags=["Google Drive"])

# Google Drive models
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

# Dependency to get Google Drive service
def get_drive_service():
    try:
        return get_service()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to Google Drive: {str(e)}"
        )

# Google Drive CRUD endpoints

@router.get("/files", response_model=FileListResponse)
async def list_drive_files(
    page_size: int = 10,
    service = Depends(get_drive_service)
):
    """List files from Google Drive."""
    try:
        files_data = list_files(service, page_size=page_size)
        files = [
            DriveFile(
                id=file.get("id", ""),
                name=file.get("name", ""),
                mime_type=file.get("mimeType", ""),
                size=file.get("size"),
                modified_time=file.get("modifiedTime")
            )
            for file in files_data
        ]
        return FileListResponse(files=files, count=len(files))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )

@router.get("/folders", response_model=FileListResponse)
async def list_drive_folders(
    page_size: int = 10,
    service = Depends(get_drive_service)
):
    """List folders from Google Drive."""
    try:
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.folder'",
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        files_data = results.get("files", [])
        folders = [
            DriveFile(
                id=file.get("id", ""),
                name=file.get("name", ""),
                mime_type=file.get("mimeType", ""),
                modified_time=file.get("modifiedTime")
            )
            for file in files_data
        ]
        return FileListResponse(files=folders, count=len(folders))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list folders: {str(e)}"
        )

@router.post("/files", response_model=UploadResponse)
async def upload_drive_file(
    file: UploadFile = File(...),
    parent_folder_id: Optional[str] = None,
    service = Depends(get_drive_service)
):
    """Upload a file to Google Drive."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Upload to Google Drive
            result = upload_file(
                service, 
                tmp_file_path, 
                mime_type=file.content_type,
                parent_folder_id=parent_folder_id,
                file_name=file.filename
            )
            
            return UploadResponse(
                id=result.get("id", ""),
                name=result.get("name", ""),
                mime_type=result.get("mimeType", ""),
                message="File uploaded successfully"
            )
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/files/{file_id}/download")
async def download_drive_file(
    file_id: str,
    service = Depends(get_drive_service)
):
    """Download a file from Google Drive."""
    try:
        # Get file metadata
        file_metadata = service.files().get(fileId=file_id, fields="name, mimeType").execute()
        file_name = file_metadata.get("name", "download")
        
        # Create temporary file for download
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file_name}") as tmp_file:
            tmp_file_path = tmp_file.name

        # Download file from Google Drive
        download_file(service, file_id, tmp_file_path)
        
        # Return file as response
        def cleanup_file():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        
        return FileResponse(
            path=tmp_file_path,
            filename=file_name,
            media_type=file_metadata.get("mimeType", "application/octet-stream"),
            background=cleanup_file
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )

@router.delete("/files/{file_id}", response_model=DeleteResponse)
async def delete_drive_file(
    file_id: str,
    service = Depends(get_drive_service)
):
    """Delete a file from Google Drive."""
    try:
        # Get file name before deletion for response
        file_metadata = service.files().get(fileId=file_id, fields="name").execute()
        file_name = file_metadata.get("name", "unknown")
        
        # Delete the file
        delete_file(service, file_id)
        
        return DeleteResponse(
            message=f"File '{file_name}' deleted successfully",
            file_id=file_id
        )
        
    except Exception as e:
        if "File not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with ID {file_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.get("/files/{file_id}", response_model=DriveFile)
async def get_file_metadata(
    file_id: str,
    service = Depends(get_drive_service)
):
    """Get metadata for a specific file."""
    try:
        file_metadata = service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, size, modifiedTime"
        ).execute()
        
        return DriveFile(
            id=file_metadata.get("id", ""),
            name=file_metadata.get("name", ""),
            mime_type=file_metadata.get("mimeType", ""),
            size=file_metadata.get("size"),
            modified_time=file_metadata.get("modifiedTime")
        )
        
    except Exception as e:
        if "File not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with ID {file_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file metadata: {str(e)}"
        )

@router.get("/search", response_model=FileListResponse)
async def search_drive_files(
    query: str,
    page_size: int = 10,
    service = Depends(get_drive_service)
):
    """Search for files in Google Drive by name."""
    try:
        search_query = f"name contains '{query}'"
        results = service.files().list(
            q=search_query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
        ).execute()
        
        files_data = results.get("files", [])
        files = [
            DriveFile(
                id=file.get("id", ""),
                name=file.get("name", ""),
                mime_type=file.get("mimeType", ""),
                size=file.get("size"),
                modified_time=file.get("modifiedTime")
            )
            for file in files_data
        ]
        return FileListResponse(files=files, count=len(files))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search files: {str(e)}"
        )