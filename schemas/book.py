
from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    cover_image: str | None = None
    sort_order: int = 0

class BookUpdate(BaseModel):
    title: str | None= None
    cover_image: str | None = None
    sort_order: int | None = None

class BookResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str = Field(...)
    title: str = Field(...)
    cover_image: str | None = Field(...)
    sort_order: int = Field(...)
    memory_count: int = Field(...)
    created_at: str = Field(...)
