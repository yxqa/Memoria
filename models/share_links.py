from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ShareLink(Base):
    __tablename__ = 'share_links'

    id: Mapped[str] = mapped_column(String(36),primary_key=True)
    memory_id: Mapped[str] = mapped_column(String(36),ForeignKey("memories.id"))
    user_id: Mapped[str] = mapped_column(String(36),ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String(128),unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expire_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)