import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("GEMINI_API_KEY")

def generate_next_action(data):
    genai.configure(api_key=TOKEN)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        f"summarize to single line for each thing email and events for next 3 hours data: {data}"
    )

    # 處理回應
    if response:
        return response.text
    else:
        return {"error": "Failed to generate action"}

if __name__ == "__main__":
    data = "your email and event data here"
    print(generate_next_action(data))
