import os
from random import choice, randint
import dbfuncs as dbf
import sqlite3
import google.generativeai as genai


conn = sqlite3.connect('bill.db')
c = conn.cursor()

allowed_keys = ["no", "money", "method", "note"]

genai.configure(api_key=[os.getenv("GEMINI_API_KEY")])
model = genai.GenerativeModel("gemini-1.5-flash")

# response = model.generate_content("Write a 30 words story about a magic backpack.")
# print(response.text)

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()
    if lowered == '':
        return 'Well, you\'re awfully silent...'
    
    elif lowered.split()[0] == "bill":
        _, money, method, note = list(lowered.split())
        c.execute("SELECT COUNT(*) FROM bills")
        row_count = c.fetchone()[0]
        results = dbf.insert_bill(row_count+1, money, method, note)
        search_result = dbf.search_bill(None, "no", row_count+1)
        if results:
            return f"bill successly added!   {search_result}"
    
    elif lowered.split()[0] == "search":
        _, key, value = list(lowered.split())
        if key not in allowed_keys:
            return "Invalid search key."
        result = dbf.search_bill(_, key, value)
        return f"here is your result! {result}"

    elif lowered.split()[0] == "delete":
        _, key, value = list(lowered.split())
        if key != "no":
            return "please give me no"
        result = dbf.delete_bill(_, key, value)
        return result

    elif lowered == "roll dice":
        return f"you rolled {randint(1,6)}"
    
    elif lowered.split()[0] == "translate":
        response = model.generate_content(f"trnaslate text into {lowered.split()[1]} language: {lowered.split()[2:]}")
        return response.text

    else:
        return choice(['I do not understand...',
                        'What are you talking about?',
                        'Do you mind rephrasing that?'])