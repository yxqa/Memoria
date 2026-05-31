from pydantic import BaseModel, Field


class ShareByUser(BaseModel):
    username: str

class ShareImageItem(BaseModel):
    url: str
    upload_order: int


class ShareCreate(BaseModel):
    expire_hours: int | None = Field(default=24,ge=1, lt=48)
    password: str | None = Field(default=None, max_length=10, min_length=4)

class ShareResponse(BaseModel):
    model_config = {"from_attributes": True}
    share_id: str
    share_url: str
    token: str
    expire_at: str
    has_password: bool
    created_at: str

class ShareAccessMemory(BaseModel):
    id: str
    content: str | None
    mood: str | None
    location: str | None
    happened_at: str | None
    tags: list[str]

class ShareAccessResponse(BaseModel):
    memory: ShareAccessMemory
    images: list[ShareImageItem]
    video: ShareImageItem | None = None
    shared_by: ShareByUser
    expire_at: str
