from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import json

from app.services.prompt_service import (
    preview_ai_data,
    process_ai_prompt,
    generate_audio_for_words,
    generate_flashcards_bulk,
    generate_flashcard_video,
    FLASHCARD_DIR,
    VIDEO_DIR,
    PROCESS_DIR,
)

# Biến cục bộ để lưu ngôn ngữ đã chọn
_word_lang: str = "English"  # Giá trị mặc định
_meaning_lang: str = "Vietnamese" # Giá trị mặc định

router = APIRouter()
# Pydantic model for AI prompt request
class AIPromptRequest(BaseModel):
    user_prompt: str
    word_lang: str
    meaning_lang: str
    level: str
    words_num: int

# Endpoint to generate word list from AI
@router.post("/generate_word_list")
async def generate_word_list(request_data: AIPromptRequest):
    global _word_lang
    global _meaning_lang
    try:
        words_dict = process_ai_prompt(
            request_data.user_prompt,
            request_data.word_lang,
            request_data.meaning_lang,
            request_data.level,
            request_data.words_num
        )
        _word_lang = request_data.word_lang
        _meaning_lang = request_data.meaning_lang
        return {"message": "Đã tạo danh sách từ vựng từ AI thành công.", "words": words_dict}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi tạo danh sách từ vựng từ AI: {e}")

# Router to view file contents
@router.get("/viewAIPrompt")
async def view_doc():
    return preview_ai_data()

# Endpoint to generate audio for the generated word list
@router.post("/generate_ai_audio")
async def generate_ai_audio():
    try:
        file_path = PROCESS_DIR / 'PromptAns.json'
        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy file dữ liệu prompt.")
        with open(file_path, 'r', encoding='utf-8') as json_file:
            words_dict = json.load(json_file).get("words", {})

        audio_paths = generate_audio_for_words(words_dict, _word_lang)
        return {"message": "Đã tạo audio cho danh sách từ vựng thành công.", "audio_paths": audio_paths}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi tạo audio từ danh sách AI: {e}")

# Endpoint to generate flashcards from the generated word list
@router.post("/generate_ai_flashcards")
async def generate_ai_flashcards():
    try:
        file_path = PROCESS_DIR / 'PromptAns.json'
        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy file dữ liệu prompt.")
        with open(file_path, 'r', encoding='utf-8') as json_file:
            words_dict = json.load(json_file)

        flashcard_paths = generate_flashcards_bulk(words_dict)
        return {"message": "Đã tạo flashcards từ danh sách từ vựng thành công.", "flashcard_paths": flashcard_paths}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi tạo flashcards từ danh sách AI: {e}")

# Endpoint to generate video
@router.post("/generate_flashcard_video")
async def generate_flashcard_video_with_audio():
    try:
        file_path = PROCESS_DIR / 'PromptAns.json'
        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy file dữ liệu prompt.")
        with open(file_path, 'r', encoding='utf-8') as json_file:
            words_data = json.load(json_file)

        video_path = generate_flashcard_video(words_data)
        return {
            "message": "Video with audio generated successfully",
            "video_path": video_path,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate video with audio: {str(e)}")

# Endpoint to download video
@router.get("/download/video/{filename}")
async def download_video(filename: str):
    video_path = VIDEO_DIR / filename
    if not video_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return FileResponse(path=str(video_path), filename=filename, media_type="video/mp4")
