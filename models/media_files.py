from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum
from models.base import Base


class FileType(str, PyEnum):
    IMAGE = "image"
    VIDEO = "video"

class MediaFile(Base):
    __tablename__ = "media_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    memory_id: Mapped[str] = mapped_column(String(36), ForeignKey("memories.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    file_type: Mapped[FileType] = mapped_column(String(10), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_order: Mapped[int] = mapped_column(Integer, nullable=False)