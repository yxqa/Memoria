from enum import Enum

from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"



class ExportTaskCreateResponse(BaseModel):
    model_config = {"from_attributes": True}

    task_id: str
    status: str = Field(default="pending")
    created_at: str

class ExportTaskResponse(BaseModel):
    model_config = {"from_attributes": True}

    task_id: str
    status: TaskStatus
    download_url: str | None = None
    error_msg: str | None = None
    created_at: str
    completed_at: str | None = None
