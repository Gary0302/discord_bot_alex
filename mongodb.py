from pymongo import MongoClient
import os
import logging
from urllib.parse import quote_plus

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger("pymongo").setLevel(logging.WARNING)


# Initialize MongoDB connection
client = MongoClient("mongodb://localhost:27017/Alex_db")
db = client['Alex']  # Database name
collection = db['processed_data']  # Collection name

def setup_mongo():
    try:
        client.admin.command('ping')  # Send a ping command to ensure connection works
        logger.info("Successfully connected to MongoDB.")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False

# Save processed IDs
def save_processed_data(emails, events):
    if emails:
        collection.update_one({"type": "emails"}, {"$addToSet": {"ids": {"$each": emails}}}, upsert=True)
    if events:
        collection.update_one({"type": "events"}, {"$addToSet": {"ids": {"$each": events}}}, upsert=True)

# Get processed IDs
def get_processed_data():
    email_data = collection.find_one({"type": "emails"})
    event_data = collection.find_one({"type": "events"})
    return {
        "emails": set(email_data['ids']) if email_data else set(),
        "events": set(event_data['ids']) if event_data else set()
    }