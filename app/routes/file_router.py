from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Body
from pathlib import Path
from pydantic import BaseModel
from app.services.file_service import validate_and_save_file,delete_file,update_file
from app.services.languages import Language
from app.services.post_uploaded import *
from app.services.prompt_service import process_ai_prompt
from app.services.sound_service import generate_audio_files

router = APIRouter()

#Tạo các folders và make sure là nó tồn tại
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

PROCESS_DIR = Path("processed")
PROCESS_DIR.mkdir(exist_ok=True)

#Router upload file
@router.post("/uploadDoc")
async def upload_doc(file: UploadFile = File(...)):
    return validate_and_save_file(file, UPLOAD_DIR)

#Router xóa file khi user cancel
@router.delete("/deleteDoc")
async def delete_doc(filename: str):
    return delete_file(filename, UPLOAD_DIR)

#Phần edit file sau upload (updating ...)
class UpdateRequest(BaseModel):
    updates: list  # List of dictionaries containing new words & meanings

@router.put("/updateDoc")
async def update_doc(filename: str, request: UpdateRequest):
    return update_file(filename, request.updates, UPLOAD_DIR)

#Router xử lí data sau khi upload (excel -> json)
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
    
class AIPromptRequest(BaseModel):
    user_prompt: str
    word_lang: str
    meaning_lang: str
    level: str
    words_num: int
    
#Router prompt AI
@router.post("/process_ai_prompt")
async def process_ai_prompt_route(request_data: AIPromptRequest):
    words_dict = process_ai_prompt(
        request_data.user_prompt,
        request_data.word_lang,
        request_data.meaning_lang,
        request_data.level,
        request_data.words_num
    )
    return {"message": "Đã xử lý prompt AI thành công", "data": words_dict}

#Router create sound
@router.post("/generate_audio")
async def generate_audio(language: str = Body(embed=True)):
    audio_files = generate_audio_files(language)
    return {"message": "Audio files generated successfully", "audio_files": audio_files}
