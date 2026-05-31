from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum

from models.base import Base



class TaskStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ExportTask(Base):
    __tablename__ = "export_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    status: Mapped[TaskStatus] = mapped_column(String(20), nullable=False, default=TaskStatus.PENDING)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_msg: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)