from fastapi import APIRouter, File, UploadFile, HTTPException, Body
from pathlib import Path

from pydantic import BaseModel

from app.services.file_service import validate_and_save_file,delete_file,update_file
from app.services.post_uploaded import *

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the upload directory exists

PROCESS_DIR = Path("processed")
PROCESS_DIR.mkdir(exist_ok=True) # Ensure the processed directory exists


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

@router.post("/processData")
async def process_data(filename: str = Body(embed=True)):
    try:
        file_path = Path("uploads") / filename  # Create the full path.
        data_dict = data_to_dict(str(file_path))
        save_dict_to_json(data_dict, filename)
        return data_dict
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

