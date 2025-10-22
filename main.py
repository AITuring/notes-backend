from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from models import NoteIn, NoteOut
import crud
from db import fs_bucket,client, db  # 复用你现有的 MongoDB 客户端和数据库句柄
from bson import ObjectId
from typing import List
from models import NoteUpdate, ImagesAppend

app = FastAPI(title='Note API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def root():
    return {"message": "FastAPI connected to MongoDB!"}

@app.post("/notes", response_model=NoteOut)
async def create_note_endpoint(note: NoteIn):
    doc = await crud.create_note(note.dict())
    return NoteOut(
        id=doc["id"],
        title=doc["title"],
        content=doc["content"],
        images=doc["images"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )

@app.get("/notes", response_model=List[NoteOut])
async def list_notes():
    notes = await crud.get_notes()
    return notes

@app.get("/notes/{id}", response_model=NoteOut)
async def get_note(id: str):
    note = await crud.get_note(id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.patch("/notes/{id}", response_model=NoteOut)
async def update_note_endpoint(id: str, payload: NoteUpdate):
    updated = await crud.update_note(id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated

@app.delete("/notes/{id}")
async def delete_note_endpoint(id: str):
    deleted = await crud.delete_note(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return Response(status_code=204)

@app.post("/notes/{id}/images", response_model=NoteOut)
async def append_images_endpoint(id: str, payload: ImagesAppend):
    if not payload.image_ids:
        raise HTTPException(status_code=422, detail="image_ids cannot be empty")
    note = await crud.append_images(id, payload.image_ids)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    content = await file.read()
    file_id = await fs_bucket.upload_from_stream(
        filename=file.filename,
        source=content,
        metadata={"contentType": file.content_type},
    )
    return {"image_id": str(file_id)}


@app.get("/image/{image_id}")
async def get_image(image_id: str):
    oid = ObjectId(image_id)
    try:
        grid_out = await fs_bucket.open_download_stream(oid)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")
    data = await grid_out.read()
    ct = getattr(grid_out, "content_type", None)
    if not ct and getattr(grid_out, "metadata", None):
        ct = grid_out.metadata.get("contentType")
    headers = {"Content-Type": ct or "application/octet-stream"}
    return Response(content=data, headers=headers, media_type=ct or "application/octet-stream")

