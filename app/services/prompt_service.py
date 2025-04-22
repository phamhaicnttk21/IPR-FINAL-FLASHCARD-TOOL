import json
import os
from pathlib import Path
import re
from google import genai
from fastapi import HTTPException, status
from gtts import gTTS
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import logging
from app.services.languages import Language
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

# Initialize Google AI Client
client = genai.Client(api_key='AIzaSyDlzm1meQUJDM74s_MbaeW28s2I0m6U-iQ')

# Directories
PROCESS_DIR = Path("processed")
PROCESS_DIR.mkdir(exist_ok=True)
AUDIO_AIPROMPT_DIR = Path("audio_aiPrompt")
AUDIO_AIPROMPT_DIR.mkdir(exist_ok=True)
FLASHCARD_DIR = Path("flashcards")
FLASHCARD_DIR.mkdir(exist_ok=True)
VIDEO_DIR = Path("videos")
VIDEO_DIR.mkdir(exist_ok=True)
BACKGROUND_IMAGE_PATH = Path("./background_img/background.jpg")

# Pexels API configuration
PEXELS_API_KEY = "kdGXOScusJGzlHdi2azPw8U0L0H4Pq2Nks7IAmNra5ZLnIDBaJT2eF36"
PEXELS_API_URL = "https://api.pexels.com/v1/search"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_ai_prompt(user_prompt: str, word_lang: str, meaning_lang: str, level: str, words_num: int) -> dict:
    try:
        # Tạo prompt cho AI
        ai_prompt = (f"{user_prompt}. Tạo cho tôi {words_num} từ mới tiếng {word_lang} có nghĩa tương ứng bằng tiếng {meaning_lang} ở trình độ {level}."
                     "Chỉ trả về nội dung. Mỗi dòng chỉ chứa một từ mới và một nghĩa, được ngăn cách bằng dấu phẩy.")

        # Gọi API Google AI
        response = client.models.generate_content(model="gemini-2.0-flash", contents=ai_prompt)
        ai_text = response.text.strip()

        # Phân tích phản hồi
        words_dict = {}
        lines = [line.strip() for line in ai_text.strip().split('\n') if line.strip()]  # Loại bỏ dòng trống
        if not lines:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không nhận được phản hồi từ AI.")

        for line in lines:
            parts = line.split(',')
            if meaning_lang.lower() == 'chinese':
                if len(parts) > 0:
                    word = parts[0].strip()
                    meaning = ','.join(parts[1:]).strip() if len(parts) > 1 else ""
                    words_dict[word] = meaning
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Định dạng dòng không hợp lệ từ AI (tiếng Trung): {line}")
            elif len(parts) == 2:
                word, meaning = parts
                words_dict[word.strip()] = meaning.strip()
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Định dạng dòng không hợp lệ từ AI: {line}")

        # Lưu kết quả trực tiếp vào JSON
        result_data = {"words": words_dict, "word_lang": word_lang}
        file_path = PROCESS_DIR / 'PromptAns.json'
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(result_data, json_file, ensure_ascii=False, indent=4)  # Thêm indent cho dễ đọc

        return words_dict

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi xử lý prompt AI: {e}")

def preview_ai_data() -> dict:
    filename = "PromptAns.json"
    file_path = PROCESS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)  # Load the entire JSON structure

        words_data = data.get("words", {})  # Safely extract the "words" dictionary

        if not isinstance(words_data, dict):
            raise HTTPException(
                status_code=400,
                detail="Invalid data format: 'words' should be a dictionary.",
            )

        result = []
        word_count = 1
        for word, meaning in words_data.items():
            audio_path = AUDIO_AIPROMPT_DIR / f"word{word_count}.mp3"
            audio_path_str = str(audio_path) if audio_path.exists() else None
            result.append({"Word": word, "Meaning": meaning, "audio_path": audio_path_str})
            word_count += 1
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read or process file: {e}"
        )

def generate_audio_for_words(words_dict: dict, word_lang: str) -> dict:
    audio_paths = {"words": {}, "meanings": {}}
    word_count = 1

    print(f"Words dict in generate_audio: {words_dict}")
    for word, meaning in words_dict.items():
        try:
            # Tạo audio cho word
            word_lang_enum = Language[word_lang.upper()]
            tts_word = gTTS(text=word, lang=word_lang_enum.value, slow=False)
            word_audio_filename = f"word{word_count}.mp3"
            word_audio_path = AUDIO_AIPROMPT_DIR / word_audio_filename
            tts_word.save(str(word_audio_path))
            audio_paths["words"][word] = str(word_audio_path)
            print(f"Đã lưu audio cho từ '{word}' ({word_lang}) tại {word_audio_path}")
            word_count += 1

        except KeyError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ngôn ngữ không được hỗ trợ: {e}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi tạo audio cho '{word}': {e}")

    return audio_paths

def generate_flashcards_bulk(words_data: dict) -> list:
    flashcard_paths = []
    words_dict = words_data.get("words", {})  # Lấy dictionary 'words' từ dữ liệu
    flashcard_count = 1

    if not words_dict:
        logger.warning("Không có từ vựng nào để tạo flashcards.")
        return flashcard_paths
    for word, meaning in words_dict.items():
        image = None
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            params = {"query": word, "per_page": 1, "orientation": "landscape"}
            response = requests.get(PEXELS_API_URL, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("photos"):
                    image_url = data["photos"][0]["src"]["medium"]
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        image = Image.open(io.BytesIO(image_response.content)).convert("RGB")

        except Exception as e:
            logger.error(f"Lỗi khi tương tác với Pexels cho '{word}': {e}")

        if image is None:
            try:
                image = Image.open(BACKGROUND_IMAGE_PATH).convert("RGB")
                logger.warning(f"Không tìm thấy ảnh Pexels cho '{word}', sử dụng ảnh background.")
            except FileNotFoundError:
                logger.error(f"Không tìm thấy ảnh background tại: {BACKGROUND_IMAGE_PATH}")
                continue
            except Exception as e:
                logger.error(f"Lỗi khi mở ảnh background: {e}")
                continue

        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("./Font_Noto_Sans_SC/NotoSansSC.ttf", 40)
        except IOError:
            logger.warning("Không tìm thấy font Noto Sans CJK SC, sử dụng font mặc định.")
            font = ImageFont.load_default()

        word_text = f"Word: {word}"
        meaning_text = f"Meaning: {meaning}"
        word_bbox = draw.textbbox((0, 0), word_text, font=font)
        meaning_bbox = draw.textbbox((0, 0), meaning_text, font=font)

        image_width, image_height = image.size
        word_x = (image_width - (word_bbox[2] - word_bbox[0])) / 2
        word_y = image_height - 200
        meaning_x = (image_width - (meaning_bbox[2] - meaning_bbox[0])) / 2
        meaning_y = image_height - 150

        draw.text((word_x + 2, word_y + 2), word_text, font=font, fill="black")
        draw.text((word_x, word_y), word_text, font=font, fill="white")
        draw.text((meaning_x + 2, meaning_y + 2), meaning_text, font=font, fill="black")
        draw.text((meaning_x, meaning_y), meaning_text, font=font, fill="white")

        flashcard_filename = f"flashcard{flashcard_count}.jpg"
        flashcard_path = FLASHCARD_DIR / flashcard_filename
        image.save(flashcard_path, "JPEG")
        flashcard_paths.append(str(flashcard_path))
        print(f"Đã tạo flashcard cho '{word}' tại {flashcard_path}")
        flashcard_count += 1

    return flashcard_paths

def generate_flashcard_video(words_data: dict):
    logger.info("Bắt đầu quá trình tạo video flashcard có âm thanh (sử dụng moviepy và đọc audio theo thứ tự).")
    image_files = sorted([f for f in FLASHCARD_DIR.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')])
    logger.info(f"Found image files: {[f.name for f in image_files]}")

    if not image_files:
        logger.warning("Không tìm thấy ảnh trong thư mục flashcards.")
        raise HTTPException(status_code=404, detail="Không tìm thấy ảnh trong thư mục flashcards.")
    try:
        words_data = preview_ai_data()
    except Exception as e:
        logger.error(f"Failed to get word data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get word data: {e}")

    video_clips = []
    audio_clips = []
    word_list = list(words_data.get("words", {}).keys())
    num_words = len(word_list)

    for i in range(min(num_words, len(image_files))):
        image_path = str(image_files[i])
        word = words_data[i]["Word"]
        audio_path = words_data[i]["audio_path"]

        try:
            image_clip = ImageClip(image_path, duration=5)
            if audio_path:
                logger.info(f"Đọc file audio word: {audio_path}")
                if not os.path.exists(audio_path):  # Import os
                    logger.error(f"File audio không tồn tại: {audio_path}")
                    continue  # Skip từ này nếu file không tồn tại
                try:
                    word_audio_clip = AudioFileClip(audio_path)
                    final_clip = image_clip.set_audio(word_audio_clip)
                    video_clips.append(final_clip)
                    audio_clips.append(word_audio_clip)  # Keep track of audio clips to close
                except Exception as e:
                    logger.error(f"Lỗi khi đọc file audio '{audio_path}': {e}")
                    raise HTTPException(status_code=500, detail=f"Lỗi khi đọc file audio '{audio_path}': {e}")
            else:
                logger.warning(f"Không tìm thấy file audio cho từ '{word}'. Sử dụng ảnh không có âm thanh.")
                video_clips.append(image_clip)

        except Exception as e:
            logger.error(f"Lỗi khi xử lý file thứ {i + 1}: {e}")
            raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý file thứ {i + 1}: {e}")

    if not video_clips:
        logger.error("Không có clip nào được tạo.")
        raise HTTPException(status_code=500, detail="Không có clip nào được tạo.")

    final_video = concatenate_videoclips(video_clips, method="compose")
    output_path = VIDEO_DIR / "flashcard_video_with_audio.mp4"
    try:
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec="mpeg4",
            audio_codec="aac",
            audio_bitrate="128k"
        )
        logger.info(f"Video có âm thanh đã được tạo tại {output_path}")
        return str(output_path)
    except Exception as e:
        logger.error(f"Lỗi khi ghi video có âm thanh: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi ghi video có âm thanh: {e}")
    finally:
        # Giải phóng tài nguyên
        final_video.close()
        for clip in audio_clips:
            clip.close()
