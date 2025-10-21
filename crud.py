from db import fs_bucket,db
from datetime import datetime
from bson import ObjectId
import base64
from pymongo import ReturnDocument

async def create_note(data: dict) :
    now = datetime.now()
    doc = {
        "title": data["title"],
        "content": data["content"],
        "images": data.get("images", []),
        "created_at": now,
        "updated_at": now,
    }

    res = await db.notes.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    return doc

async def get_notes():
    cursor = db.notes.find().sort("updated_at", -1)
    res = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        res.append(doc)
    return res

async def get_note(id: str):
    try:
        oid = ObjectId(id)
    except Exception:
        return None
    doc = await db.notes.find_one({"_id": oid})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

async def update_note(id: str, data: dict):
    try:
        oid = ObjectId(id)
    except Exception:
        return None
    update_fields = {}
    if "title" in data and data["title"] is not None:
        update_fields["title"] = data["title"]
    if "content" in data and data["content"] is not None:
        update_fields["content"] = data["content"]
    update_fields["updated_at"] = datetime.now()
    doc = await db.notes.find_one_and_update(
        {"_id": oid},
        {"$set": update_fields},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

async def delete_note(id: str) -> bool:
    try:
        oid = ObjectId(id)
    except Exception:
        return False
    res = await db.notes.delete_one({"_id": oid})
    return res.deleted_count == 1

async def append_images(id: str, image_ids: list[str]):
    try:
        oid = ObjectId(id)
    except Exception:
        return None
    # 追加并去重
    await db.notes.update_one(
        {"_id": oid},
        {"$addToSet": {"images": {"$each": image_ids}}},
    )
    return await get_note(id)
