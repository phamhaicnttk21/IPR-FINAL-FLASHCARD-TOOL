from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
from app.services.file_service import validate_and_save_file

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/uploadDoc")
async def upload_doc(file: UploadFile = File(...)):
    return validate_and_save_file(file, UPLOAD_DIR)
