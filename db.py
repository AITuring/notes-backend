import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

load_dotenv()

# Prefer full URI via MONGODB_URI; fallback to MONGO_URL + MONGO_DB
MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB")
DEFAULT_DB = os.getenv("MONGODB_DATABASE") or "notes"

if MONGODB_URI:
    client = AsyncIOMotorClient(MONGODB_URI)
    default_db = client.get_default_database()
    db = default_db if default_db is not None else client[MONGO_DB or DEFAULT_DB]
elif MONGO_URL and MONGO_DB:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB]
else:
    raise RuntimeError("Missing MongoDB configuration. Set MONGODB_URI or MONGO_URL + MONGO_DB.")

# GridFS bucket for images
fs_bucket = AsyncIOMotorGridFSBucket(db)
