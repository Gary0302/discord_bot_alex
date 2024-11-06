from Bill import bill
import sqlite3



def insert_bill(no:int, money:int, method:str, note:str):
    with sqlite3.connect('bill.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO bills values (?, ?, ?, ?, ?)",(no, money, method, note, True))
        return True





def search_bill(_, key, value):
    with sqlite3.connect('bill.db') as conn:
        c = conn.cursor()
        query = f"SELECT * FROM bills WHERE {key} = ?"
        if key in ["method", "note"]:  # 假設這些是字符串類型
            c.execute(query, (str(value),))
        else:
            c.execute(query, (int(value),))

        results = list(c.fetchall())

        if not results:
            return "no data qq"
        elif results[-1][-1] == 0:
            return "this bill has been deleted"
        else:
            results = ' '.join(map(str, results))
            results = results[1::].split(", ")[:-1:]
            print(results)
            return f"\nNo.{results[0]}\nMoney: {results[1]}\nMethod: {results[2]}\nNote: {results[3]}"

def delete_bill(_, key, value):
    with sqlite3.connect('bill.db') as conn:
        c = conn.cursor()

        c.execute(f"SELECT * FROM bills WHERE {key} = ?", (int(value),))
        results = list(c.fetchall())
        if not results:
            return "no data qq"
        else:
            c.execute("""UPDATE bills
                      SET Active_flag = False
                      WHERE no = ?""", (value))
            return f"bill deleted!"
