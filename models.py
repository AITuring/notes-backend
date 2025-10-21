from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class NoteIn(BaseModel):
    title: str
    content: str

class NoteOut(BaseModel):
    id: str
    title: str
    content: str
    images: List[str] = []
    created_at: datetime
    updated_at: datetime

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class ImagesAppend(BaseModel):
    image_ids: List[str] = Field(default_factory=list)