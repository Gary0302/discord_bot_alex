import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/Alex_db")

# MongoDB client
client = None

def setup_mongo():
    """
    Set up the MongoDB client and test the connection.
    """
    global client
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')  # Test connection
        logger.info("Successfully connected to MongoDB.")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False

def get_config():
    """
    Retrieve the configuration from the database.
    If no configuration exists, return a default configuration.
    """
    if not client:
        logger.error("MongoDB client not initialized.")
        return {"type": "config", "duration": None}

    db = client["ai_assistant"]
    collection = db["config"]
    config = collection.find_one({"type": "config"})
    return config if config else {"type": "config", "duration": None}

def save_config(duration):
    """
    Save the configuration to the database.
    """
    if not client:
        logger.error("MongoDB client not initialized.")
        return

    db = client["ai_assistant"]
    collection = db["config"]
    collection.update_one(
        {"type": "config"},
        {"$set": {"duration": duration}},
        upsert=True
    )
    logger.info(f"Configuration saved: {duration} hours.")

def start_ui():
    """
    Placeholder function for starting the UI setup.
    """
    logger.info("Starting UI setup...")
    print("UI placeholder - replace with actual implementation.")

# Define a default global variable for bot_running
bot_running = True
