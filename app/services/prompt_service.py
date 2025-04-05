import json
import os
import re
from pathlib import Path
from google import genai
from fastapi import HTTPException, status

PROCESS_DIR = Path("processed")
PROCESS_DIR.mkdir(exist_ok=True)

# Initialize Google AI Client
client = genai.Client(api_key="AIzaSyDlzm1meQUJDM74s_MbaeW28s2I0m6U-iQ")

def process_ai_prompt(user_prompt: str):
    try:
        # Tạo prompt cho AI
        ai_prompt = user_prompt + (
            "Tôi cần làm flashcard. Hãy tạo cho tôi tối đa 10 từ mới và nghĩa tương ứng. "
            "Mỗi dòng chỉ chứa một từ mới và một nghĩa, phải đủ cả word và meaning, ngăn cách bằng dấu phẩy. "
            "Vui lòng định dạng kết quả dưới dạng CSV và không cần ghi thêm gì khác."
        )

        # Gọi API Google AI
        response = client.models.generate_content(model="gemini-2.0-flash", contents=ai_prompt)
        ai_text = response.text.strip()

        # Phân tích phản hồi
        words_dict = {}
        lines = ai_text.strip().split('\n')
        if len(lines) <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid AI response format.")

        for line in lines[1:]:
            parts = line.split(',')
            if len(parts) == 2:
                word, meaning = parts
                words_dict[word.strip()] = meaning.strip()
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid line in AI response: {line}")

        # Lưu kết quả vào JSON
        file_path = PROCESS_DIR / 'PromptAns.json'
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(words_dict, json_file, ensure_ascii=False)

        return words_dict

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")