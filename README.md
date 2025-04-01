Guide to start 

source /mnt/e/IPR-FINAL-FLASHCARD-TOOL/.venv/bin/activate

1. Clone to local : git clone git@github.com:phamhaicnttk21/IPR-FINAL-FLASHCARD-TOOL.git
2. Install appropriate package : pip install fastapi uvicorn pandas openpyxl gTTS
3. Run commmand : pip install -q -U google-genai
4. Start app : uvicorn main:app --reload
5. Access api doc locally: 127.0.0.8000/docs 



Guide to Test feature Prompt AI to generate word: 
1. cd to the location of prompt_service.py (cd app/services)
2. Run command : python prompt_service.py


Guide to test post_uploaded process:
1. Start app : uvicorn main:app --reload
2. Open postman run post request (http://127.0.0.1:8000/home/processData)
3. Enter body raw with this content:
{
    "filename": "Book1.xlsx"
}

4. Output will appear in the processed folder