import json
import os
import re
from pathlib import Path
from google import genai

PROCESS_DIR = Path("processed")
PROCESS_DIR.mkdir(exist_ok=True)

# Initialize Google AI Client
client = genai.Client(api_key="AIzaSyDlzm1meQUJDM74s_MbaeW28s2I0m6U-iQ")

# Get user input
user_prompt = input("Ask anything: ")
task = "Tôi cần làm flashcard hãy tạo cho tôi 1 từ mới và 1 nghĩa. Max là 10 từ nhé"
user_prompt2 = user_prompt + task + "Tôi sẽ cần định dạng csv chỉ chứ 1 new word và 1 meaning, được ngăn cách bằng dấu phẩy. Ngoài ra đừng ghi thêm gì"

# Generate AI response
response = client.models.generate_content(model="gemini-2.0-flash", contents=user_prompt2)

# Ensure response is in JSON format
ai_text = response.text.strip()
print(ai_text)

# Phân tích chuỗi phản hồi
words_dict = {}
lines = ai_text.strip().split('\n')

# Bỏ qua dòng tiêu đề và xử lý các dòng tiếp theo
for line in lines[1:]:
    word, meaning = line.split(',')
    words_dict[word.strip()] = meaning.strip()

# Lưu kết quả vào file JSON
file_path = os.path.join(PROCESS_DIR, 'PromptAns.json')
with open(file_path, 'w', encoding='utf-8') as json_file:
    json.dump(words_dict, json_file, ensure_ascii=False)

print(f"Response saved to {file_path}")
