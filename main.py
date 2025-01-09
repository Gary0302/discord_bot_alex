import logging
import os
from dotenv import load_dotenv, find_dotenv, get_key
import schedule
import time
from gmail_handler import get_recent_emails
from calendar_handler import get_upcoming_events
from gemini_handler import generate_next_action
from discord.ext import commands, tasks
from discord import Intents, Client
from mongodb import get_processed_data, save_processed_data
import asyncio
import subprocess
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import tkinter as tk
from config import get_config, start_ui, bot_running, setup_mongo
import threading
import json
# 載入環境變數
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/calendar.readonly']

# 設置 Discord 客戶端
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)

# 設定日誌
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
logging.getLogger("googleapiclient.discovery").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定時任務
# Keep track of sent items
sent_emails = set()
sent_events = set()

# 全域憑證變數
creds = None

async def refresh_credentials():
    global creds
    if os.path.exists(find_dotenv()):
        try:
            creds_json = get_key(find_dotenv(),'GOOGLE_CREDENTIALS')
            creds = Credentials.from_authorized_user_info(info=json.loads(creds_json), scopes=SCOPES)
            logger.info("Credentials loaded from .env")
        except Exception as e:
            logger.error(f"Failed to load credentials from .env: {e}")

    if not creds or not creds.valid:
        logger.info("Credentials not found or invalid, attempting to refresh/create credentials.")
        try:
            result = subprocess.run(['python3', 'refresh_token.py'], check=True, capture_output=True, text=True)
            if result.returncode == 0:
                 logger.info("Google API credentials refreshed/created successfully.")
            else:
                 logger.error(f"Failed to refresh Google API credentials. Error: {result.stderr}")
                 exit()
        except Exception as e:
           logger.error(f"Failed to run refresh_token.py: {e}")
           exit()
    
    elif creds and creds.expired and creds.refresh_token:
            logger.info("Credentials has expired, attempting to refresh credentials.")
            try:
              result = subprocess.run(['python3', 'refresh_token.py'], check=True, capture_output=True, text=True)
              if result.returncode == 0:
                  logger.info("Google API credentials refreshed successfully.")
              else:
                logger.error(f"Failed to refresh Google API credentials. Error: {result.stderr}")
                exit()
            except Exception as e:
                logger.error(f"Failed to run refresh_token.py: {e}")
                exit()

async def create_gmail_service():
    global creds
    if not creds:
        await refresh_credentials()
    return build('gmail', 'v1', credentials=creds)

async def create_calendar_service():
    global creds
    if not creds:
        await refresh_credentials()
    return build('calendar', 'v3', credentials=creds)

async def main():
    if not start_ui():
        print("UI setup failed, stopping bot.")
        return
    
    # Rest of your bot startup code


async def scheduled_task(channel):
    logger.info("Fetching new data...")

    try:
        # Get previously processed data
        processed_data = get_processed_data()
        processed_emails = processed_data['emails']
        processed_events = processed_data['events']
        logger.debug(f"Processed emails: {processed_emails}, processed events: {processed_events}")
        # Fetch current data
        gmail_service = await create_gmail_service()
        calendar_service = await create_calendar_service()
        emails = get_recent_emails(gmail_service)
        events = get_upcoming_events(calendar_service)
        logger.debug(f"Fetched emails: {emails}, fetched events: {events}")
        # Filter new items
        new_emails = [email for email in emails if email['id'] not in processed_emails]
        new_events = [event for event in events if event['id'] not in processed_events]
        logger.debug(f"New emails: {new_emails}, new events: {new_events}")
        # Update MongoDB
        save_processed_data(
            emails=[email['id'] for email in new_emails],
            events=[event['id'] for event in new_events]
        )
        logger.info(f"Updated MongoDB with new emails: {[email['id'] for email in new_emails]}, new events: {[event['id'] for event in new_events]}")
        # Generate and send suggestions if there's new data
        if new_emails or new_events:
            suggestion = generate_next_action({"emails": new_emails, "events": new_events})
            if "error" not in suggestion:
                message = f"Next 30 Minutes Suggestion:\n{suggestion}"
                await channel.send(message)
                logger.info(f"Successfully send discord message: {message}")
            else:
                logger.error("Failed to generate suggestion.")
        else:
            logger.info("No new data to send.")

    except RefreshError as e:
        logger.error(f"Error during scheduled task with Google API: {e}")
        logger.info("Attempting to refresh Google API credentials...")
        try:
           result = subprocess.run(['python3', 'refresh_token.py'], check=True, capture_output=True, text=True)
           if result.returncode == 0:
              logger.info("Google API credentials refreshed successfully.")
           else:
              logger.error(f"Failed to refresh Google API credentials. Error: {result.stderr}")
              exit()
        except Exception as e:
            logger.error(f"Failed to run refresh_token.py: {e}")
            exit()
        #如果成功刷新憑證，則再次執行任務
        await scheduled_task(channel)
    except Exception as e:
        logger.error(f"Error during scheduled task: {e}", exc_info=True)


    # Discord Bot 啟動
async def start_discord_bot():
    @client.event
    async def on_ready():
        print(f"Discord Bot Logged in as {client.user}")
        
        # 獲取伺服器的第一個可用頻道
        if len(client.guilds) > 0:
            guild = client.guilds[0]
            if len(guild.text_channels) > 0:
                channel = guild.text_channels[0]  # 假設我們發送訊息到第一個頻道
                # 啟動排程
                @tasks.loop(minutes=30)
                async def loop_task():
                    await scheduled_task(channel)

                loop_task.start()
                logger.info("Scheduled task started")
            else:
                logger.warning("No text channels available in this server.")
        else:
            logger.warning("Bot is not connected to any server.")
        # 首次啟動時 刷新凭证
        await refresh_credentials()

    await client.start(TOKEN)  # 使用 .env 檔案中的 Discord Token

if __name__ == "__main__":
    print("Starting Alex with Discord Integration...")
    if not setup_mongo():
        print("Database connection failed, stopping bot.")
        exit()
    start_ui()
    asyncio.run(start_discord_bot())
    while bot_running:
        time.sleep(1)
    print("Bot stopped")