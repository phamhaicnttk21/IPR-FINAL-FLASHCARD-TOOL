from google import genai
from gtts import gTTS
import os
import playsound
import nltk
from nltk.corpus import words
from langdetect import detect

# Download the NLTK English words dataset (only needed once)
nltk.download("words")
english_vocab = set(words.words())  # Load English vocabulary

# Initialize Google AI Client
client = genai.Client(api_key="AIzaSyDlzm1meQUJDM74s_MbaeW28s2I0m6U-iQ")

# Get user input
user_prompt = input("Ask anything: ")

# Generate AI response
response = client.models.generate_content(model="gemini-2.0-flash", contents=user_prompt)

# Ensure response is in JSON format
ai_text = response.text.strip()
response_json = {"original_text": ai_text}  # Returning a JSON format
print(response_json)  # Debugging

# Split into words
words_list = ai_text.split()

# Create a folder to store MP3 files
audio_folder = "audio_files"
os.makedirs(audio_folder, exist_ok=True)

saved_files = []
for index, word in enumerate(words_list):
    try:
        # Check if the word is in the English vocabulary OR detected as English
        if word.lower() in english_vocab or detect(word) == "en":
            audio_file = os.path.join(audio_folder, f"word_{index + 1}.mp3")
            tts = gTTS(text=word, lang="en")
            tts.save(audio_file)
            saved_files.append(audio_file)
            print(f"✅ Saved: {audio_file}")
        else:
            print(f"❌ Skipping non-English word: {word}")

    except Exception as e:
        print(f"⚠️ Error processing word '{word}': {e}")

# Play each saved MP3 file sequentially using playsound
for audio_file in saved_files:
    playsound.playsound(audio_file)

print("🎵✅ All words processed and played successfully!")

# Optional cleanup: Delete MP3 files after playing
for file in saved_files:
    os.remove(file)
print("🗑 Audio files deleted.")
