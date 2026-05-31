from datetime import datetime

from sqlalchemy import String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class MemoryBook(Base):
    __tablename__ = 'memory_books'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id") ,nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)