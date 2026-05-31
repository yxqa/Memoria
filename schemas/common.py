
from pydantic import BaseModel, Field


class PaginatedResponse(BaseModel):
    items: list
    total: int = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total_pages: int = Field(...)

class ErrorResponse(BaseModel):
    detail: str
    code: str
