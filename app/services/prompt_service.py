from google import genai
from gtts import gTTS
import os
import playsound

# Initialize Google AI Client
client = genai.Client(api_key="AIzaSyDlzm1meQUJDM74s_MbaeW28s2I0m6U-iQ")

# Get user input
user_prompt = input("Ask anything: ")

# Generate AI response
response = client.models.generate_content(model="gemini-2.0-flash", contents=user_prompt)

# Ensure response is in JSON format
ai_text = response.text.strip()
response_json = {"original_text": ai_text}
print(response_json)  # Debugging

# Split the text into lines
lines = ai_text.split('\n')

# Create a folder to store MP3 files
audio_folder = "audio_files"
os.makedirs(audio_folder, exist_ok=True)

saved_files = []
phrase_counter = 1  # To ensure sequential numbering from 1 to 10

for line in lines:
    # Skip empty lines
    if not line.strip():
        continue

    # Look for lines that start with a number and contain a collocation (e.g., "1. **Go on a date:**")
    if line.strip().startswith(tuple(str(i) + '.' for i in range(1, 11))) and '**' in line:
        try:
            # Extract the phrase between ** and **, and remove the trailing colon if present
            english_phrase = line.split('**')[1].strip()  # Get text between first and second **
            if english_phrase.endswith(':'):
                english_phrase = english_phrase[:-1]  # Remove trailing colon

            # Save the audio file with sequential numbering
            audio_file = os.path.join(audio_folder, f"phrase_{phrase_counter}.mp3")
            tts = gTTS(text=english_phrase, lang="en")
            tts.save(audio_file)
            saved_files.append(audio_file)
            print(f"✅ Saved: {audio_file} - Phrase: '{english_phrase}'")
            phrase_counter += 1  # Increment for the next phrase

        except IndexError:
            print(f"❌ Skipping malformed line: {line}")
        except Exception as e:
            print(f"⚠️ Error processing phrase in line '{line}': {e}")
    else:
        print(f"❌ Skipping non-collocation line: {line}")

# Play each saved MP3 file sequentially using playsound
for audio_file in saved_files:
    try:
        playsound.playsound(audio_file)
    except Exception as e:
        print(f"⚠️ Error playing {audio_file}: {e}")

print("🎵✅ All phrases processed and played successfully!")