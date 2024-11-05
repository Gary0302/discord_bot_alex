import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response
import sqlite3
from Bill import bill
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents : Intents = Intents.default()
intents.message_content = True
client : Client = Client(intents=intents)


conn = sqlite3.connect('bill.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bills';")
if c.fetchone() is None:
    c.execute("""CREATE TABLE bills (
              no INTEGER PRIMARY KEY,
              money INTEGER NOT NULL,
              method TEXT NOT NULL,
              note TEXT,
              Active_flag BOOLEAN NOT NULL DEFAULT 1
    )""")
conn.commit()
conn.close()














async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()