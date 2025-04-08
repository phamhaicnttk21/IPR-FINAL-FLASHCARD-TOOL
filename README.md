Guide to start 

source /mnt/e/IPR-FINAL-FLASHCARD-TOOL/.venv/bin/activate

1. Clone to local : git clone git@github.com:phamhaicnttk21/IPR-FINAL-FLASHCARD-TOOL.git
2. Install appropriate package : pip install fastapi uvicorn pandas openpyxl gTTS
3. Run commmand : pip install -q -U google-genai
4. Start app : uvicorn main:app --reload
5. Access api doc locally: 127.0.0.8000/docs 


Test prompt
Start app : uvicorn main:app --reload
2. Open postman run post request (http://127.0.0.1:8000/home/process_ai_prompt)
3. Enter body raw with this content:
{
    "user_prompt": "Cho tôi từ mới chủ đề lời chào tiếng Trung - Tiếng Việt"
}


Guide to test post_uploaded process:
1. Start app : uvicorn main:app --reload
2. Open postman run post request (http://127.0.0.1:8000/home/processData)
3. Enter body raw with this content:
{
    "filename": "Book1.xlsx"
}

4. Output will appear in the processed folder

Test gen voice
1. Start app : uvicorn main:app --reload
2. Open postman run post request (http://127.0.0.1:8000/home/generate_audio)
3. Enter body raw with this content:
{
  "language": "Chinese"
}
4. Output will appear in the audio folder
