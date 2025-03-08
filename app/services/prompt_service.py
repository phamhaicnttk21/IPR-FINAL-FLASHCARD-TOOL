from google import genai

client = genai.Client(api_key="AIzaSyDlzm1meQUJDM74s_MbaeW28s2I0m6U-iQ")
user_prompt  = input("Ask anything:" + "")
response = client.models.generate_content(
    model="gemini-2.0-flash", contents=user_prompt
)
print(response.text +" " + "Let me know if you need help")