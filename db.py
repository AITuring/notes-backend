from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "notes_demo")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
fs_bucket = AsyncIOMotorGridFSBucket(db)  # GridFS bucket for images
