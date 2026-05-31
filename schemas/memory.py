from fastapi import UploadFile
from pydantic import BaseModel


class MediaItem(BaseModel):
    id: str
    url: str
    upload_order: int
    file_size: int | None = None



class MemoryCreate(BaseModel):
    content: str | None = None
    mood: str | None = None
    location: str | None = None
    happened_at: str | None = None
    book_id: str | None = None
    tags: str | None = None
    #不支持图片视频文件
    # images: list[UploadFile] | None = None
    # video: UploadFile | None = None

class MemoryUpdate(BaseModel):
    content: str | None = None
    mood: str | None = None
    location: str | None = None
    happened_at: str | None = None
    book_id: str | None = ""
    tags: list[str] | None = None

class MemoryDetail(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    content: str | None
    mood: str | None
    location: str | None
    happened_at: str | None
    book_id: str | None
    book_title: str | None
    tags: list[str]
    images: list[MediaItem]
    video: MediaItem | None
    created_at: str
    updated_at: str

class MemoryListItem(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    content: str | None
    mood: str | None
    location: str | None
    happened_at: str | None
    book_id: str | None
    tags: list[str]
    image_count: int
    has_video: bool
    created_at: str

class TagSyncRequest(BaseModel):
    tags: list[str]

class TagSyncResponse(BaseModel):
    tags: list[str]


class SearchResultItem(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    content: str | None
    mood: str | None
    relevance: float
    created_at: str

class MemoryCreateResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    content: str | None
    mood: str | None
    location: str | None
    happened_at: str | None
    book_id: str | None
    tags: list[str]
    images: list[MediaItem]
    video: MediaItem | None
    created_at: str
    updated_at: str