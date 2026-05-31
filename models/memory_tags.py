from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class MemoryTag(Base):
    __tablename__ = "memory_tags"

    memory_id: Mapped[str] = mapped_column(String(36), ForeignKey("memories.id"), primary_key=True)
    tag_id: Mapped[str] = mapped_column(String(36), ForeignKey("tags.id"), primary_key=True)