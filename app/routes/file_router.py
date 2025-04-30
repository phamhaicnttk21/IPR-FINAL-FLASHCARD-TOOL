import os
import re
from typing import Dict, List
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
from moviepy import VideoClip, AudioFileClip, concatenate_videoclips
import numpy as np
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Get the directory of the current script
BASE_DIR = Path(__file__).parent

FLASHCARD_AI_FOLDER = BASE_DIR / "flashcard_ai_prompt"
FLASHCARD_AI_FOLDER.mkdir(exist_ok=True)

# Directories
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESS_DIR = BASE_DIR / "processed"
PROCESS_DIR.mkdir(exist_ok=True)
AUDIO_UPLOADFILE_DIR = BASE_DIR / "audio_uploadfile"
AUDIO_UPLOADFILE_DIR.mkdir(exist_ok=True)
AUDIO_AIPROMPT_DIR = BASE_DIR / "audio_aiPrompt"
AUDIO_AIPROMPT_DIR.mkdir(exist_ok=True)
FLASHCARD_DIR = BASE_DIR / "flashcards"
FLASHCARD_DIR.mkdir(exist_ok=True)
VIDEO_DIR = BASE_DIR / "videos"
VIDEO_DIR.mkdir(exist_ok=True)

# Pexels API configuration
PEXELS_API_KEY = "QUOXZECGj4TtyTuEIX4Q6wguNFompHCzBlTE46KLTzeFcqBg1Pc6UfKy"
PEXELS_API_URL = "https://api.pexels.com/v1/search"

# Language mapping dictionary
LANGUAGE_MAP = {
    "english": "en",
    "vietnamese": "vi",
    "tiếng việt": "vi",
}

# List of supported languages by gTTS
SUPPORTED_LANGUAGES = set(LANGUAGE_MAP.values())

# Pydantic model for individual update items
class UpdateItem(BaseModel):
    Word: str
    Meaning: str

# Pydantic model for the update request
class UpdateRequest(BaseModel):
    updates: list[UpdateItem]

# Pydantic model for AI prompt request
class AIPromptRequest(BaseModel):
    user_prompt: str
    word_lang: str
    meaning_lang: str
    level: str
    words_num: int
    save_images: bool = False
    image_folder: str = "flashcard_ai_prompt"

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
        required_columns = ["Word", "Meaning"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"Excel file must contain columns: {', '.join(required_columns)}"
            )
        data = df[required_columns].to_dict(orient="records")
        return data
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

def clean_field(field: str) -> str:
    try:
        import ast
        parsed = ast.literal_eval(field)
        if isinstance(parsed, tuple) and len(parsed) == 2 and parsed[0] in ('Word', 'Meaning'):
            value = parsed[1]
            while isinstance(value, str):
                try:
                    nested_parsed = ast.literal_eval(value)
                    if isinstance(nested_parsed, tuple) and len(nested_parsed) == 2 and nested_parsed[0] in ('Word', 'Meaning'):
                        value = nested_parsed[1]
                    else:
                        break
                except (ValueError, SyntaxError):
                    break
            return value
        return field
    except (ValueError, SyntaxError):
        pattern = r"\('(?:Word|Meaning)', '([^']+)'\)|\('(?:Word|Meaning)', '\\?'(?:Word|Meaning)\\?', \"\\?'(?:Word|Meaning)\\?', '([^']+)'\)\"\)"
        match = re.search(pattern, field)
        if match:
            return match.group(1) if match.group(1) else match.group(2)
        return field.strip("'\"")

def update_file(filename: str, updates: list, upload_dir: Path) -> dict:
    file_path = upload_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_excel(file_path, engine="openpyxl")
        required_columns = ["Word", "Meaning"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"Excel file must contain columns: {', '.join(required_columns)}"
            )
        
        cleaned_updates = []
        for update in updates:
            cleaned_word = clean_field(update.Word)
            cleaned_meaning = clean_field(update.Meaning)
            cleaned_updates.append({"Word": cleaned_word, "Meaning": cleaned_meaning})
        
        logger.info(f"Received updates (cleaned): {cleaned_updates}")
        new_df = pd.DataFrame(cleaned_updates, columns=["Word", "Meaning"])
        
        if list(new_df.columns) != required_columns:
            raise HTTPException(
                status_code=400,
                detail="Updates must contain exactly 'Word' and 'Meaning' columns"
            )
        
        logger.info(f"Saving DataFrame: {new_df.to_dict(orient='records')}")
        new_df.to_excel(file_path, index=False, engine="openpyxl")
        return {"message": f"File {filename} updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")

def process_ai_prompt(user_prompt: str, word_lang: str, meaning_lang: str, level: str, words_num: int) -> Dict[str, List[Dict[str, str]]]:
    supported_languages = {
        "english": "en",
        "vietnamese": "vi",
        "french": "fr",
        "spanish": "es"
    }

    if word_lang.lower() not in supported_languages:
        raise HTTPException(status_code=400, detail=f"Unsupported word language: {word_lang}")
    word_lang_code = supported_languages[word_lang.lower()]

    if meaning_lang.lower() not in supported_languages:
        raise HTTPException(status_code=400, detail=f"Unsupported meaning language: {meaning_lang}")
    meaning_lang_code = supported_languages[meaning_lang.lower()]

    if level.lower() not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail=f"Unsupported level: {level}")

    user_prompt_lower = user_prompt.lower().strip()
    words = re.findall(r'\b\w+\b', user_prompt_lower)
    stop_words = {"on", "the", "a", "an", "in", "to", "for", "and", "or", "with", "about", "words", "topic", "give", "me"}
    keywords = [word for word in words if word not in stop_words and len(word) > 2]

    if not keywords:
        raise HTTPException(status_code=400, detail="No meaningful keywords found in prompt")

    primary_keyword = keywords[0]

    def generate_related_words(keyword: str, level: str, max_count: int) -> List[str]:
        base_words = [keyword]
        level_extensions = {
            "beginner": [
                f"{keyword}land",
                f"{keyword}scape",
                f"{keyword}field"
            ],
            "intermediate": [
                f"{keyword}land",
                f"{keyword}scape",
                f"{keyword}field",
                f"{keyword}area",
                f"{keyword}zone"
            ],
            "advanced": [
                f"{keyword}land",
                f"{keyword}scape",
                f"{keyword}field",
                f"{keyword}area",
                f"{keyword}zone",
                f"{keyword}region",
                f"{keyword}space",
                f"{keyword}form"
            ]
        }
        related_terms = level_extensions[level.lower()]
        base_words.extend([term for term in related_terms if len(term) > 3][:max_count-1])
        return base_words[:max_count]

    max_words = {
        "beginner": 5,
        "intermediate": 8,
        "advanced": 12
    }.get(level.lower(), 5)

    base_words = generate_related_words(primary_keyword, level, max_words)

    def get_mock_meaning(word: str, lang_code: str) -> str:
        if lang_code == "en":
            return word.capitalize()
        lang_names = {
            "vi": "Tiếng Việt",
            "fr": "Français",
            "es": "Español"
        }
        lang_name = lang_names.get(lang_code, lang_code.upper())
        return f"{word.capitalize()} ({lang_name})"

    generated_words = []
    for word in base_words[:min(max_words, words_num)]:
        meaning = get_mock_meaning(word, meaning_lang_code)
        generated_words.append({
            "word": word.capitalize(),
            "meaning": meaning
        })

    while len(generated_words) < words_num:
        extra_word = f"{primary_keyword}{len(generated_words) + 1}"
        meaning = get_mock_meaning(extra_word, meaning_lang_code)
        generated_words.append({
            "word": extra_word.capitalize(),
            "meaning": meaning
        })

    return {"data": generated_words[:words_num]}

def generate_audio_files(language: str) -> list:
    return []

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

@router.post("/uploadDoc", summary="Upload Excel File")
async def upload_doc(file: UploadFile = File(...)):
    return validate_and_save_file(file, UPLOAD_DIR)

@router.get("/listFiles", summary="List Uploaded Files")
async def list_uploaded_files():
    try:
        files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
        if not files:
            return {"message": "No files found", "files": []}
        return {"message": "Files retrieved successfully", "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.get("/viewDoc", summary="View Excel File Contents")
async def view_doc(filename: str):
    return read_file_contents(filename, UPLOAD_DIR)

@router.delete("/deleteDoc", summary="Delete Excel File")
async def delete_doc(filename: str):
    return delete_file(filename, UPLOAD_DIR)

@router.put("/updateDoc", summary="Update Excel File")
async def update_doc(filename: str, request: UpdateRequest):
    try:
        result = update_file(filename, request.updates, UPLOAD_DIR)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")

@router.post("/processData", summary="Process Excel Data to JSON")
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

@router.post("/process_ai_prompt", summary="Process AI Prompt for Word Generation")
async def process_ai_prompt_route(request_data: AIPromptRequest):
    try:
        word_lang = request_data.word_lang.lower()
        meaning_lang = request_data.meaning_lang.lower()

        word_lang_code = LANGUAGE_MAP.get(word_lang)
        meaning_lang_code = LANGUAGE_MAP.get(meaning_lang)

        if not word_lang_code:
            logger.error(f"Unsupported word language: {word_lang}")
            raise HTTPException(status_code=400, detail=f"Unsupported word language: {word_lang}")
        if not meaning_lang_code:
            logger.error(f"Unsupported meaning language: {meaning_lang}")
            raise HTTPException(status_code=400, detail=f"Unsupported meaning language: {meaning_lang}")

        if word_lang_code not in SUPPORTED_LANGUAGES:
            logger.error(f"Language not supported by gTTS: {word_lang_code}")
            raise HTTPException(status_code=400, detail=f"Language not supported by gTTS: {word_lang_code}")
        if meaning_lang_code not in SUPPORTED_LANGUAGES:
            logger.error(f"Language not supported by gTTS: {meaning_lang_code}")
            raise HTTPException(status_code=400, detail=f"Language not supported by gTTS: {meaning_lang_code}")

        words_dict = process_ai_prompt(
            request_data.user_prompt,
            word_lang,
            meaning_lang,
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
                tts = gTTS(text=word, lang=word_lang_code, slow=False)
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

@router.post("/generate_audio", summary="Generate Audio for Words")
async def generate_audio(language: str = Body(embed=True)):
    audio_files = generate_audio_files(language)
    return {"message": "Audio files generated successfully", "audio_files": audio_files}

@router.post("/generate_audio_uploadFile", summary="Upload File and Prepare for Audio Generation")
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

@router.post("/generate_audio_for_all_files", summary="Generate Audio for All Uploaded Files")
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

async def generate_single_flashcard(word: str, meaning: str, save_images: bool = True, image_folder: str = "flashcards") -> Dict:
    """
    Generate a single flashcard image with the given word and meaning, with subtitles at the bottom and a softer background.

    Args:
        word (str): The word to display on the flashcard.
        meaning (str): The meaning to display on the flashcard.
        save_images (bool): Whether to save the generated image.
        image_folder (str): The folder to save the image in ("flashcards" or "flashcard_ai_prompt").

    Returns:
        Dict: A dictionary containing the path to the generated flashcard.
    """
    try:
        # Determine the folder to save the image
        if image_folder == "flashcard_ai_prompt":
            save_dir = FLASHCARD_AI_FOLDER
        else:
            save_dir = FLASHCARD_DIR
        save_dir.mkdir(exist_ok=True)

        # Fetch a background image from Pexels
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": word, "per_page": 1}
        response = requests.get(PEXELS_API_URL, headers=headers, params=params)
        if response.status_code != 200 or not response.json().get("photos"):
            # Fallback to a gradient background if Pexels fails
            logger.warning(f"Failed to fetch image from Pexels for word '{word}'. Using gradient background.")
            background = Image.new("RGB", (800, 600), "white")
            draw_temp = ImageDraw.Draw(background)
            for y in range(600):
                r = int(135 + (y / 600) * (66 - 135))  # Gradient from #87CEEB to #4267B2
                g = int(206 + (y / 600) * (103 - 206))
                b = int(235 + (y / 600) * (178 - 235))
                draw_temp.line([(0, y), (800, y)], fill=(r, g, b))
        else:
            photo = response.json()["photos"][0]
            image_url = photo["src"]["medium"]
            image_response = requests.get(image_url)
            background = Image.open(io.BytesIO(image_response.content)).convert("RGB")
            background = background.resize((800, 600), Image.Resampling.LANCZOS)

        # Create a draw object
        draw = ImageDraw.Draw(background)

        # Load fonts
        try:
            word_font = ImageFont.truetype("arial.ttf", 50)
            meaning_font = ImageFont.truetype("arial.ttf", 40)
        except Exception:
            try:
                word_font = ImageFont.truetype("calibri.ttf", 50)
                meaning_font = ImageFont.truetype("calibri.ttf", 40)
            except Exception:
                word_font = ImageFont.load_default()
                meaning_font = ImageFont.load_default()

        # Calculate text dimensions
        word_bbox = draw.textbbox((0, 0), word, font=word_font)
        word_width = word_bbox[2] - word_bbox[0]
        word_height = word_bbox[3] - word_bbox[1]

        meaning_bbox = draw.textbbox((0, 0), meaning, font=meaning_font)
        meaning_width = meaning_bbox[2] - meaning_bbox[0]
        meaning_height = meaning_bbox[3] - meaning_bbox[1]

        # Define spacing
        gap = 40
        text_block_height = word_height + gap + meaning_height
        total_height = 600
        bottom_margin = 20
        start_y = total_height - text_block_height - bottom_margin

        word_x = (800 - word_width) // 2
        word_y = start_y
        meaning_x = (800 - meaning_width) // 2
        meaning_y = word_y + word_height + gap

        padding = 10
        subtitle_bg_color = (240, 240, 240, 180)  # Light grey with transparency

        # Add soft background for word
        draw.rectangle(
            [(word_x - padding, word_y - padding), (word_x + word_width + padding, word_y + word_height + padding)],
            fill=subtitle_bg_color
        )
        # Word shadow and text
        draw.text((word_x + 2, word_y + 2), word, font=word_font, fill=(50, 50, 50))
        draw.text((word_x, word_y), word, font=word_font, fill="black")

        # Add soft background for meaning
        draw.rectangle(
            [(meaning_x - padding, meaning_y - padding), (meaning_x + meaning_width + padding, meaning_y + meaning_height + padding)],
            fill=subtitle_bg_color
        )
        # Meaning shadow and text
        draw.text((meaning_x + 2, meaning_y + 2), meaning, font=meaning_font, fill=(50, 50, 50))
        draw.text((meaning_x, meaning_y), meaning, font=meaning_font, fill="black")

        # Save the flashcard image
        safe_word = "".join(c if c.isalnum() else "_" for c in word)
        flashcard_filename = f"Word_{safe_word}_flashcard.jpg"
        flashcard_path = save_dir / flashcard_filename

        if save_images:
            background.save(flashcard_path, "JPEG")
            logger.info(f"Flashcard saved at {flashcard_path}")
        else:
            logger.info(f"Flashcard generated but not saved (save_images=False)")

        return {
            "word": word,
            "meaning": meaning,
            "flashcard_path": str(flashcard_path)
        }

    except Exception as e:
        logger.error(f"Failed to generate flashcard for word '{word}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcard for word '{word}'.")


@router.get("/generate_flashcard", summary="Generate Single Flashcard")
async def generate_flashcard(word: str, meaning: str):
    return await generate_single_flashcard(word, meaning)

@router.post("/generate_ai_flashcards", summary="Generate Flashcards from AI Prompt")
async def generate_flashcards(request_data: AIPromptRequest):
    try:
        words_dict = process_ai_prompt(
            request_data.user_prompt,
            request_data.word_lang.lower(),
            request_data.meaning_lang.lower(),
            request_data.level,
            request_data.words_num
        )

        flashcard_results = []
        for item in words_dict["data"]:
            word = item.get("word")
            meaning = item.get("meaning")
            if not word or not isinstance(word, str) or not meaning or not isinstance(meaning, str):
                logger.warning(f"Skipping invalid word-meaning pair: {word} - {meaning}")
                continue
            flashcard_result = await generate_single_flashcard(
                word, 
                meaning, 
                save_images=request_data.save_images, 
                image_folder=request_data.image_folder
            )
            flashcard_results.append(flashcard_result)

        return {
            "message": "Flashcards generated successfully",
            "flashcards": flashcard_results
        }
    except Exception as e:
        logger.error(f"Failed to generate flashcards: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")

@router.get("/home/download_flashcard", summary="Download Flashcard Image")
async def download_flashcard(filename: str):
    try:
        flashcard_path = FLASHCARD_AI_FOLDER / filename
        if not flashcard_path.exists():
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

@router.get("/get_flashcard_ai_images", summary="Get AI-Generated Flashcard Images")
async def get_flashcard_ai_images():
    try:
        files = os.listdir(FLASHCARD_AI_FOLDER)
        image_files = [f"/flashcard_ai_prompt/{f}" for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
        return {"images": image_files}
    except Exception as e:
        return {"error": str(e)}

async def generate_audio_for_words(words: List[str], language: str, audio_dir: Path) -> List[str]:
    audio_files = []
    try:
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
        logger.error(f"Failed to generate audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

async def generate_flashcards_for_data(data: List[Dict[str, str]], save_images: bool = True) -> List[Dict]:
    flashcard_results = []
    for item in data:
        word = item.get("Word")
        meaning = item.get("Meaning")
        if not word or not isinstance(word, str) or not meaning or not isinstance(meaning, str):
            logger.warning(f"Skipping invalid word-meaning pair: {word} - {meaning}")
            continue
        flashcard_result = await generate_single_flashcard(
            word,
            meaning,
            save_images=save_images,
            image_folder="flashcards"
        )
        flashcard_results.append(flashcard_result)
    return flashcard_results

@router.post("/generate_audio_for_file", summary="Generate Audio for Words in Excel File")
async def generate_audio_for_file(filename: str = Form(...), language: str = Form("en")):
    try:
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            logger.error(f"File not found: {filename}")
            raise HTTPException(status_code=404, detail="File not found.")

        df = pd.read_excel(file_path, engine="openpyxl")
        required_columns = ["Word", "Meaning"]
        columns_lower = [col.lower() for col in df.columns]
        column_map = {}
        for req_col in required_columns:
            for i, col in enumerate(columns_lower):
                if col == req_col.lower():
                    column_map[df.columns[i]] = req_col
        if len(column_map) != len(required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"Excel file must contain columns: {', '.join(required_columns)}"
            )
        df = df.rename(columns=column_map)
        words = df["Word"].astype(str).tolist()
        audio_files = []

        for word in words:
            if not word or not isinstance(word, str):
                logger.warning(f"Skipping invalid word: {word}")
                continue
            safe_word = "".join(c if c.isalnum() else "_" for c in word)
            audio_path = AUDIO_UPLOADFILE_DIR / f"{safe_word}.mp3"

            logger.info(f"Generating audio for word: {word}")
            tts = gTTS(text=word, lang=language, slow=False)
            tts.save(str(audio_path))

            audio_files.append(str(audio_path))

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

@router.post("/generate_flashcard_video_with_audio", summary="Generate Video with Flashcards and Audio")
async def generate_flashcard_video_with_audio(filename: str = Form(...), language: str = Form("en")):
    """Generate a video by chaining all images in flashcards folder with audio from audio_uploadfile, ensuring 5-second gaps between audio starts."""
    try:
        # Validate language
        language_map = {"english": "en", "vietnamese": "vi", "tiếng việt": "vi"}
        language_code = language_map.get(language.lower())
        if not language_code:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

        # Read all images from flashcards folder
        image_files = sorted([f for f in FLASHCARD_DIR.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')])
        if not image_files:
            raise HTTPException(status_code=404, detail="No images found in flashcards folder")
        logger.info(f"Found images: {[f.name for f in image_files]}")

        # Extract words from image filenames
        words = []
        image_paths = []
        for img_file in image_files:
            img_path = str(img_file)
            match = re.search(r'__Word____(.+?)___flashcard\.jpg|Word_(.+?)_flashcard\.jpg|(.+?)_flashcard\.jpg', img_file.name, re.IGNORECASE)
            if match:
                word = next(group for group in match.groups() if group is not None)
            else:
                word = img_file.stem.replace('_flashcard', '')
                logger.warning(f"Unrecognized name format for {img_file.name}, using fallback word: {word}")
            words.append(word)
            image_paths.append(img_path)

        if not image_paths:
            raise HTTPException(status_code=404, detail="No images found after processing")
        logger.info(f"Processed images: {image_paths}")
        logger.info(f"Extracted words: {words}")

        # Match audio files from audio_uploadfile folder
        audio_files = []
        for word in words:
            safe_word = "".join(c if c.isalnum() else "_" for c in word)
            audio_path = AUDIO_UPLOADFILE_DIR / f"{safe_word}.mp3"
            if not audio_path.exists():
                audio_path = AUDIO_UPLOADFILE_DIR / f"__Word____{safe_word}__.mp3"
            if audio_path.exists():
                audio_files.append(str(audio_path))
                logger.info(f"Found audio for word {word}: {audio_path}")
            else:
                logger.warning(f"No audio file found for word {word} in audio_uploadfile")
                audio_files.append(None)
        logger.info(f"Audio files: {audio_files}")

        # Generate video with audio, ensuring 5-second gaps between audio starts
        clip_duration = 5  # Fixed duration for each clip
        clips = []
        for img_path, audio_path, word in zip(image_paths, audio_files, words):
            img = cv2.imread(img_path)
            if img is None:
                logger.warning(f"Failed to read image: {img_path}, skipping")
                continue
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_array = np.array(img_rgb)
            logger.info(f"Loaded image {img_path} with shape: {img_array.shape}")

            def make_frame(t, frame_data=img_array):
                return frame_data

            clip = VideoClip(make_frame, duration=clip_duration)

            if audio_path:
                try:
                    audio_clip = AudioFileClip(audio_path)
                    logger.info(f"Audio duration for {audio_path}: {audio_clip.duration}")
                    clip.audio = audio_clip
                    clips.append(clip)
                except Exception as e:
                    logger.warning(f"Failed to add audio for {word}: {str(e)}")
                    clips.append(clip)
                    if 'audio_clip' in locals():
                        audio_clip.close()
            else:
                clips.append(clip)

        if not clips:
            raise HTTPException(status_code=500, detail="No valid clips generated")

        final_clip = concatenate_videoclips(clips, method="compose")
        output_path = VIDEO_DIR / f"flashcard_video_{filename.split('.')[0]}.mp4"
        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=30
        )
        final_clip.close()
        for clip in clips:
            clip.close()

        if not output_path.exists():
            raise HTTPException(status_code=500, detail="Failed to create video file")

        logger.info(f"Video with audio created at {output_path}")
        return FileResponse(
            path=output_path,
            filename=f"flashcard_video_{filename.split('.')[0]}.mp4",
            media_type="video/mp4"
        )

    except Exception as e:
        logger.error(f"Failed to generate video with audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video with audio: {str(e)}")

@router.post("/generate_flashcards_for_file", summary="Generate Flashcards from Excel File")
async def generate_flashcards_for_file(filename: str = Form(...)):
    """Generate flashcards for all words in a specified Excel file."""
    try:
        data = read_file_contents(filename, UPLOAD_DIR)
        if not data:
            raise HTTPException(status_code=404, detail="No data found in the file")

        flashcard_results = []
        for item in data:
            word = item.get("Word")
            meaning = item.get("Meaning")
            if not word or not isinstance(word, str) or not meaning or not isinstance(meaning, str):
                logger.warning(f"Skipping invalid word-meaning pair: {word} - {meaning}")
                continue
            flashcard_result = await generate_single_flashcard(
                word,
                meaning,
                save_images=True,
                image_folder="flashcards"
            )
            flashcard_results.append(flashcard_result)

        if not flashcard_results:
            raise HTTPException(status_code=500, detail="No flashcards generated")

        return {
            "message": "Flashcards generated successfully",
            "flashcards": flashcard_results
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to generate flashcards for file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")