from fastapi import APIRouter, UploadFile, File


router = APIRouter()

@router.get("/upload")
async def uploadFile(file: UploadFile = File(...)):
    return await file.read()


