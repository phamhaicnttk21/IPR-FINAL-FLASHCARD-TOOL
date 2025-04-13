from fastapi import APIRouter, File, UploadFile, HTTPException, Body, Form
from pathlib import Path
from pydantic import BaseModel
from app.services.file_service import read_file_contents, validate_and_save_file, delete_file, update_file
from app.services.languages import Language
from app.services.post_uploaded import *
from app.services.prompt_service import process_ai_prompt
from app.services.sound_service import generate_audio_files
from fastapi import status
from gtts import gTTS
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Create directories if they don't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

PROCESS_DIR = Path("processed")
PROCESS_DIR.mkdir(exist_ok=True)

AUDIO_UPLOADFILE_DIR = Path("audio_uploadfile")
AUDIO_UPLOADFILE_DIR.mkdir(exist_ok=True)

AUDIO_AIPROMPT_DIR = Path("audio_aiPrompt")
AUDIO_AIPROMPT_DIR.mkdir(exist_ok=True)

# Pydantic model for individual update items
class UpdateItem(BaseModel):
    Word: str
    Meaning: str

# Pydantic model for the update request
class UpdateRequest(BaseModel):
    updates: list[UpdateItem]

# Function to generate audio from a file
async def generate_audio_from_file(filename: str, language: str, audio_dir: Path = AUDIO_UPLOADFILE_DIR):
    try:
        # Read the file from disk
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            logger.error(f"File not found: {filename}")
            raise HTTPException(status_code=404, detail="File not found.")

        df = pd.read_excel(file_path, engine="openpyxl")
        required_columns = ["Word", "Meaning"]
        if list(df.columns) != required_columns:
            logger.error(f"Invalid columns in {filename}: {list(df.columns)}")
            raise HTTPException(status_code=400, detail=f"Excel file must have exactly these columns: {required_columns}")

        words = df["Word"].tolist()
        audio_files = []

        # Generate audio for each word
        for word in words:
            if not word or not isinstance(word, str):
                logger.warning(f"Skipping invalid word: {word}")
                continue  # Skip empty or invalid words
            safe_word = "".join(c if c.isalnum() else "_" for c in word)
            audio_path = audio_dir / f"{safe_word}.mp3"

            if not audio_path.exists():
                logger.info(f"Generating audio for word: {word}")
                tts = gTTS(text=word, lang=language, slow=False)
                tts.save(str(audio_path))
            else:
                logger.info(f"Audio already exists for word: {word}")

            audio_files.append(str(audio_path))

        return audio_files
    except Exception as e:
        logger.error(f"Failed to generate audio for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

# Router to upload file (only uploads, does not generate audio)
@router.post("/uploadDoc")
async def upload_doc(file: UploadFile = File(...)):
    return validate_and_save_file(file, UPLOAD_DIR)

# Get all files in the uploads directory
@router.get("/listFiles")
async def list_uploaded_files():
    try:
        files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
        if not files:
            return {"message": "No files found", "files": []}
        return {"message": "Files retrieved successfully", "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

# Router to view file contents
@router.get("/viewDoc")
async def view_doc(filename: str):
    return read_file_contents(filename, UPLOAD_DIR)

# Router to delete file
@router.delete("/deleteDoc")
async def delete_doc(filename: str):
    return delete_file(filename, UPLOAD_DIR)

# Router to update file
@router.put("/updateDoc")
async def update_doc(filename: str, request: UpdateRequest):
    try:
        result = update_file(filename, request.updates, UPLOAD_DIR)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")

# Router to process data (excel -> json)
@router.post("/processData")
async def process_data(filename: str = Body(embed=True)):
    try:
        file_path = Path("uploads") / filename
        data_dict = data_to_dict(str(file_path))
        save_dict_to_json(data_dict, filename)
        return data_dict
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

# Pydantic model for AI prompt request
class AIPromptRequest(BaseModel):
    user_prompt: str
    word_lang: str
    meaning_lang: str
    level: str
    words_num: int

# Router for AI prompt processing
@router.post("/process_ai_prompt")
async def process_ai_prompt_route(request_data: AIPromptRequest):
    try:
        words_dict = process_ai_prompt(
            request_data.user_prompt,
            request_data.word_lang,
            request_data.meaning_lang,
            request_data.level,
            request_data.words_num
        )

        # Generate audio for AI-generated words
        audio_files = []
        for item in words_dict["data"]:  # Assuming words_dict returns {"message": ..., "data": [...]}
            word = item.get("word")  # Adjust based on actual structure of words_dict
            if not word or not isinstance(word, str):
                logger.warning(f"Skipping invalid word from AI prompt: {word}")
                continue
            safe_word = "".join(c if c.isalnum() else "_" for c in word)
            audio_path = AUDIO_AIPROMPT_DIR / f"{safe_word}.mp3"

            if not audio_path.exists():
                logger.info(f"Generating audio for AI word: {word}")
                tts = gTTS(text=word, lang=request_data.word_lang.lower(), slow=False)
                tts.save(str(audio_path))
            else:
                logger.info(f"Audio already exists for AI word: {word}")

            audio_files.append(str(audio_path))

        return {
            "message": "Đã xử lý prompt AI thành công",
            "data": words_dict["data"],
            "audio_files": audio_files
        }
    except Exception as e:
        logger.error(f"Failed to process AI prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process AI prompt: {str(e)}")

# Router to generate audio (old endpoint, can be removed if not needed)
@router.post("/generate_audio")
async def generate_audio(language: str = Body(embed=True)):
    audio_files = generate_audio_files(language)
    return {"message": "Audio files generated successfully", "audio_files": audio_files}

# Router to upload file (only uploads, does not generate audio)
@router.post("/generate_audio_uploadFile")
async def generate_audio_uploadFile(file: UploadFile = File(...), language: str = Form("en")):
    try:
        # Validate and save the file
        file_response = validate_and_save_file(file, UPLOAD_DIR)

        return {
            "filename": file_response["filename"],
            "status": "File uploaded successfully"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to process file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

# New endpoint to generate audio for all files in uploads folder
@router.post("/generate_audio_for_all_files")
async def generate_audio_for_all_files(language: str = Form("en")):
    try:
        # Get all .xlsx files in the uploads directory
        files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file() and f.name.endswith('.xlsx')]
        if not files:
            logger.info("No .xlsx files found in uploads directory")
            return {"message": "No .xlsx files found in uploads directory", "audio_files": {}}

        audio_files_dict = {}

        # Generate audio for each file
        for filename in files:
            logger.info(f"Processing file: {filename}")
            try:
                audio_files = await generate_audio_from_file(filename, language, AUDIO_UPLOADFILE_DIR)
                audio_files_dict[filename] = audio_files
            except HTTPException as e:
                logger.error(f"Failed to process {filename}: {e.detail}")
                audio_files_dict[filename] = {"error": e.detail}
            except Exception as e:
                logger.error(f"Unexpected error while processing {filename}: {str(e)}")
                audio_files_dict[filename] = {"error": str(e)}

        return {
            "message": "Audio generation completed for all files",
            "audio_files": audio_files_dict
        }
    except Exception as e:
        logger.error(f"Failed to process files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process files: {str(e)}")

# New endpoint to generate audio for a specific file
@router.post("/generate_audio_for_file")
async def generate_audio_for_file(filename: str = Form(...), language: str = Form("en")):
    try:
        # Check if the file exists
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            logger.error(f"File not found: {filename}")
            raise HTTPException(status_code=404, detail="File not found.")

        # Generate audio for the file
        audio_files = await generate_audio_from_file(filename, language, AUDIO_UPLOADFILE_DIR)

        return {
            "filename": filename,
            "status": "Audio generated successfully",
            "audio_files": audio_files
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to generate audio for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")