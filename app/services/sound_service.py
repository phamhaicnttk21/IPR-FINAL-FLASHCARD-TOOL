import json
from pathlib import Path
from annotated_types import UpperCase
from fastapi import HTTPException, status
from gtts import gTTS
import os
from app.services.languages import Language

# Tạo thư mục để lưu file âm thanh
AUDIO_FOLDER = Path("audio_files")
AUDIO_FOLDER.mkdir(exist_ok=True)

def generate_audio_files(language_input: str):
    try:
        processed_dir = Path("processed")
        json_files = list(processed_dir.glob("*.json"))

        if not json_files:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy file JSON trong thư mục 'processed'.")

        # Lấy file JSON đầu tiên tìm thấy
        file_path = json_files[0]

        with open(file_path, 'r', encoding='utf-8') as json_file:
            words_dict = json.load(json_file)

        audio_files = []
        for index, word in enumerate(words_dict.keys()):
            try:
                # Chuyển đổi input thành chữ hoa và tìm trong enum
                lang_enum = Language[language_input.upper()]
                tts = gTTS(text=word, lang=lang_enum.value)
                audio_file = AUDIO_FOLDER / f"audio{index}.mp3"
                tts.save(str(audio_file))
                audio_files.append(str(audio_file))
                print(f"Saved audio for '{word}' to {audio_file} with language: {lang_enum.value}")
            except KeyError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ngôn ngữ '{language_input}' không được hỗ trợ.")

        return audio_files

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")
