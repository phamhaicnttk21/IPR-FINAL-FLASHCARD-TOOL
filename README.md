Guide to start 

1. Clone to local : git clone git@github.com:phamhaicnttk21/IPR-FINAL-FLASHCARD-TOOL.git
2. Install appropriate package : pip install fastapi uvicorn pandas openpyxl gTTS
3. Run commmand : pip install -q -U google-genai
4. Start app : uvicorn main:app --reload
5. Access api doc locally: 127.0.0.8080/docs 



Guide to Test feature Prompt AI to generate word: 
1. cd to the location of prompt_service.py (cd app/services)
2. Run command : python prompt_service.py


