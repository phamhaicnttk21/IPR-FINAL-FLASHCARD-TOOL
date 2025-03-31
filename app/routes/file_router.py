<<<<<<< Updated upstream
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
=======
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.services.file_service import validate_and_save_file, delete_file

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the upload directory exists

# Cấu hình thư mục chứa template HTML
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def render_homepage(request: Request):
    """Trả về file index.html"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/upload", response_class=HTMLResponse)
async def render_upload_page(request: Request):
    """Trả về file upload.html"""
    return templates.TemplateResponse("uploads.html", {"request": request})

@router.get("/edit", response_class=HTMLResponse)
async def render_upload_page(request: Request):
    """Trả về file upload.html"""
    return templates.TemplateResponse("edit.html", {"request": request})

@router.post("/uploadDoc")
async def upload_doc(file: UploadFile = File(...)):
    """API upload file"""
    return validate_and_save_file(file, UPLOAD_DIR)

@router.delete("/deleteDoc")
async def delete_doc(filename: str):
    """API xóa file"""
    return delete_file(filename, UPLOAD_DIR)
>>>>>>> Stashed changes
