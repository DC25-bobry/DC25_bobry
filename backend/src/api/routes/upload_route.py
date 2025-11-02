import logging
import threading

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from backend.src.api.utils.file_validation import validate_file
from backend.src.api.services.document_parsing.document_parsing_service import DocumentParsingService

def process_file(file_bytes: bytes, filename: str, content_type: str):
    parsing_service = DocumentParsingService()
    parsed_document = parsing_service.extract_text(content=file_bytes, content_type=content_type, filename=filename)

router = APIRouter()

@router.get("/upload", response_class=HTMLResponse)
async def upload_form():
    return """
    <!doctype html>
    <title>Upload new Files</title>
    <h1>Upload new Files</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input type="file" name="files" multiple required>
      <input type="submit" value="Upload">
    </form>
    </html>
    """

@router.post("/upload", response_class=HTMLResponse)
async def upload_files(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files sent")

    for file in files:
        file_bytes = await file.read()

        file_valid, info = validate_file(file_bytes, file.filename, file.content_type)
        if not file_valid:
            raise HTTPException(status_code=400, detail=info)

        thread = threading.Thread(target=process_file, args=(file_bytes, file.filename, file.content_type,))
        thread.start()
    return HTMLResponse(content=f"Parsing {len(files)} files.")