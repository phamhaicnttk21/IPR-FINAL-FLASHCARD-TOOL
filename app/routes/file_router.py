from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path

from pydantic import BaseModel

from app.services.file_service import validate_and_save_file,delete_file,update_file

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the upload directory exists


@router.post("/uploadDoc")
async def upload_doc(file: UploadFile = File(...)):
    return validate_and_save_file(file, UPLOAD_DIR)


@router.delete("/deleteDoc")
async def delete_doc(filename: str):
    return delete_file(filename, UPLOAD_DIR)

class UpdateRequest(BaseModel):
    updates: list  # List of dictionaries containing new words & meanings

@router.put("/updateDoc")
async def update_doc(filename: str, request: UpdateRequest):
    return update_file(filename, request.updates, UPLOAD_DIR)