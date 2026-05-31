from pydantic import BaseModel


class TagResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    name: str
    usage_count: int
