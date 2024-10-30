
from random import choice, randint
import dbfuncs as dbf
import sqlite3
conn = sqlite3.connect('bill.db')
c = conn.cursor()
allowed_keys = ["no", "money", "method", "note"]


def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()
    if lowered == '':
        return 'Well, you\'re awfully silent...'
    
    if lowered.split()[0] == "bill":
        _, money, method, note = list(lowered.split())
        c.execute("SELECT COUNT(*) FROM bills")
        row_count = c.fetchone()[0]
        results = dbf.insert_bill(row_count+1, money, method, note)
        return f"bill successly added!    {' '.join(map(str, results))}"
    
    if lowered.split()[0] == "search":
        _, key, value = list(lowered.split())
        if key not in allowed_keys:
            return "Invalid search key."
        result = dbf.search_bill(_, key, value)
        return result




    if lowered.split()[0] == "delete":
        _, key, value = list(lowered.split())
        if key != "no":
            return "please give me no"
        result = dbf.delete_bill(_, key, value)
        return result

        

    if lowered == "roll dice":
        return f"you rolled {randint(1,6)}"
    else:
        return choice(['I do not understand...',
                        'What are you talking about?',
                        'Do you mind rephrasing that?'])