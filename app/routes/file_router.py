from fastapi import APIRouter, File, UploadFile, HTTPException, Body, Form
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
import pandas as pd
import logging
import requests
from PIL import Image, ImageDraw, ImageFont
import io
from gtts import gTTS
import cv2


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESS_DIR = Path("processed")
PROCESS_DIR.mkdir(exist_ok=True)
AUDIO_UPLOADFILE_DIR = Path("audio_uploadfile")
AUDIO_UPLOADFILE_DIR.mkdir(exist_ok=True)
AUDIO_AIPROMPT_DIR = Path("audio_aiPrompt")
AUDIO_AIPROMPT_DIR.mkdir(exist_ok=True)
FLASHCARD_DIR = Path("flashcards")
FLASHCARD_DIR.mkdir(exist_ok=True)


# Directories
FLASHCARD_DIR = Path("flashcards")
VIDEO_DIR = Path("videos")
VIDEO_DIR.mkdir(exist_ok=True)

# Pexels API configuration
PEXELS_API_KEY = "kdGXOScusJGzlHdi2azPw8U0L0H4Pq2Nks7IAmNra5ZLnIDBaJT2eF36"
PEXELS_API_URL = "https://api.pexels.com/v1/search"

# Pydantic model for individual update items
class UpdateItem(BaseModel):
    Word: str
    Meaning: str

# Pydantic model for the update request
class UpdateRequest(BaseModel):
    updates: list[UpdateItem]

# Placeholder for imported services (since originals are not provided)
def data_to_dict(file_path: str) -> dict:
    df = pd.read_excel(file_path, engine="openpyxl")
    return {"data": df.to_dict(orient="records")}

def save_dict_to_json(data_dict: dict, filename: str):
    import json
    output_path = PROCESS_DIR / f"{Path(filename).stem}.json"
    with open(output_path, "w") as f:
        json.dump(data_dict, f)

def validate_and_save_file(file: UploadFile, upload_dir: Path) -> dict:
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed")
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return {"filename": file.filename, "status": "File uploaded successfully"}
def read_file_contents(filename: str, upload_dir: Path) -> list:
    file_path = upload_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
    if not filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only .xlsx or .xls files are supported")
    
    try:
        df = pd.read_excel(file_path, engine="openpyxl")
        # Ensure required columns exist
        required_columns = ["Word", "Meaning"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"Excel file must contain columns: {', '.join(required_columns)}"
            )
        # Convert to list of dictionaries
        data = df[required_columns].to_dict(orient="records")
        return data  # Return list directly as specified in API
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Excel file: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to read file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

def delete_file(filename: str, upload_dir: Path) -> dict:
    file_path = upload_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    file_path.unlink()
    return {"message": f"File {filename} deleted successfully"}

def update_file(filename: str, updates: list, upload_dir: Path) -> dict:
    file_path = upload_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Read the existing Excel file
        df = pd.read_excel(file_path, engine="openpyxl")
        
        # Validate that the original file has the expected columns
        required_columns = ["Word", "Meaning"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"Excel file must contain columns: {', '.join(required_columns)}"
            )
        
        # Create a new DataFrame from updates, explicitly setting column names
        new_df = pd.DataFrame(updates, columns=["Word", "Meaning"])
        
        # Validate that updates have the correct columns
        if list(new_df.columns) != required_columns:
            raise HTTPException(
                status_code=400,
                detail="Updates must contain exactly 'Word' and 'Meaning' columns"
            )
        
        # Overwrite the file with the updated data, preserving the Excel format
        new_df.to_excel(file_path, index=False, engine="openpyxl")
        
        return {"message": f"File {filename} updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")

def process_ai_prompt(user_prompt: str, word_lang: str, meaning_lang: str, level: str, words_num: int) -> dict:
    # Mock implementation (replace with actual logic)
    return {
        "data": [
            {"word": "mock_word", "meaning": "mock_meaning"} for _ in range(words_num)
        ]
    }

def generate_audio_files(language: str) -> list:
    # Mock implementation
    return []

# Function to generate audio from a file
async def generate_audio_from_file(filename: str, language: str, audio_dir: Path = AUDIO_UPLOADFILE_DIR):
    try:
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

        for word in words:
            if not word or not isinstance(word, str):
                logger.warning(f"Skipping invalid word: {word}")
                continue
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

# Router to upload file
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
        file_path = UPLOAD_DIR / filename
        data_dict = data_to_dict(str(file_path))
        save_dict_to_json(data_dict, filename)
        return data_dict
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

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

        audio_files = []
        for item in words_dict["data"]:
            word = item.get("word")
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

# Router to generate audio (old endpoint)
@router.post("/generate_audio")
async def generate_audio(language: str = Body(embed=True)):
    audio_files = generate_audio_files(language)
    return {"message": "Audio files generated successfully", "audio_files": audio_files}

# Router to upload file and prepare for audio generation
@router.post("/generate_audio_uploadFile")
async def generate_audio_uploadFile(file: UploadFile = File(...), language: str = Form("en")):
    try:
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

# New endpoint to generate audio for all files
@router.post("/generate_audio_for_all_files")
async def generate_audio_for_all_files(language: str = Form("en")):
    try:
        files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file() and f.name.endswith('.xlsx')]
        if not files:
            logger.info("No .xlsx files found in uploads directory")
            return {"message": "No .xlsx files found in uploads directory", "audio_files": {}}

        audio_files_dict = {}
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
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            logger.error(f"File not found: {filename}")
            raise HTTPException(status_code=404, detail="File not found.")

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

@router.get("/home/generate_flashcard")
async def generate_flashcard(word: str, meaning: str):
    logger.info(f"Generating flashcard for word: {word}, meaning: {meaning}")
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": word, "per_page": 1, "orientation": "landscape"}
        response = requests.get(PEXELS_API_URL, headers=headers, params=params)
        
        if response.status_code != 200:
            logger.error(f"Pexels API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail=f"Pexels API error: {response.status_code}")

        data = response.json()
        if not data.get("photos"):
            logger.warning(f"No images found for word: {word}")
            raise HTTPException(status_code=404, detail=f"No images found for word: {word}")

        image_url = data["photos"][0]["src"]["medium"]
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            logger.error(f"Failed to download image from {image_url}")
            raise HTTPException(status_code=500, detail="Failed to download image")

        image = Image.open(io.BytesIO(image_response.content)).convert("RGB")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            logger.warning("Using default font")
            font = ImageFont.load_default()

        word_text = f"Word: {word}"
        meaning_text = f"Meaning: {meaning}"
        word_bbox = draw.textbbox((0, 0), word_text, font=font)
        meaning_bbox = draw.textbbox((0, 0), meaning_text, font=font)
        
        image_width, image_height = image.size
        word_x = (image_width - (word_bbox[2] - word_bbox[0])) / 2
        word_y = image_height - 100
        meaning_x = (image_width - (meaning_bbox[2] - meaning_bbox[0])) / 2
        meaning_y = image_height - 50

        draw.text((word_x + 2, word_y + 2), word_text, font=font, fill="black")
        draw.text((word_x, word_y), word_text, font=font, fill="white")
        draw.text((meaning_x + 2, meaning_y + 2), meaning_text, font=font, fill="black")
        draw.text((meaning_x, meaning_y), meaning_text, font=font, fill="white")

        safe_word = "".join(c if c.isalnum() else "_" for c in word)
        flashcard_path = FLASHCARD_DIR / f"{safe_word}_flashcard.jpg"
        image.save(flashcard_path, "JPEG")
        
        if not flashcard_path.exists():
            logger.error(f"Flashcard not saved at {flashcard_path}")
            raise HTTPException(status_code=500, detail="Failed to save flashcard")

        logger.info(f"Flashcard saved at {flashcard_path}")
        return {
            "message": "Flashcard generated successfully",
            "flashcard_path": str(flashcard_path),
            "word": word,
            "meaning": meaning
        }
    except Exception as e:
        logger.error(f"Error generating flashcard for {word}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcard: {str(e)}")

# New endpoint to download flashcard
@router.get("/home/download_flashcard")
async def download_flashcard(filename: str):
    try:
        flashcard_path = FLASHCARD_DIR / filename
        if not flashcard_path.exists():
            logger.error(f"Flashcard not found: {filename}")
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        return FileResponse(
            path=flashcard_path,
            filename=filename,
            media_type="image/jpeg"
        )
    except Exception as e:
        logger.error(f"Failed to download flashcard {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download flashcard: {str(e)}")
    








@router.post("/generate_flashcard_video")
async def generate_flashcard_video():
    try:
        # Get all image files from flashcards directory
        image_files = [f for f in FLASHCARD_DIR.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')]
        
        if not image_files:
            logger.warning("No images found in flashcards directory")
            raise HTTPException(status_code=404, detail="No images found in flashcards directory")

        # Read first image to get dimensions
        first_image = cv2.imread(str(image_files[0]))
        if first_image is None:
            logger.error(f"Failed to read first image: {image_files[0]}")
            raise HTTPException(status_code=500, detail="Failed to read images")
        
        height, width = first_image.shape[:2]

        # Video settings
        fps = 30  # Frames per second
        duration_per_image = 5  # seconds
        frames_per_image = fps * duration_per_image
        
        # Output video path
        output_path = VIDEO_DIR / "flashcard_video.mp4"
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        if not video_writer.isOpened():
            logger.error("Failed to initialize video writer")
            raise HTTPException(status_code=500, detail="Failed to initialize video writer")

        # Process each image
        for image_path in image_files:
            logger.info(f"Processing image: {image_path}")
            
            # Read image
            img = cv2.imread(str(image_path))
            if img is None:
                logger.warning(f"Failed to read image: {image_path}, skipping")
                continue
                
            # Resize image to match video dimensions if necessary
            img = cv2.resize(img, (width, height))
            
            # Write image frames for specified duration
            for _ in range(frames_per_image):
                video_writer.write(img)
        
        # Release video writer
        video_writer.release()
        
        if not output_path.exists():
            logger.error("Video file was not created")
            raise HTTPException(status_code=500, detail="Failed to create video file")

        logger.info(f"Video successfully created at {output_path}")
        return {
            "message": "Video generated successfully",
            "video_path": str(output_path),
            "image_count": len(image_files),
            "total_duration_seconds": len(image_files) * duration_per_image
        }

    except Exception as e:
        logger.error(f"Failed to generate video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")