from datetime import datetime

from sqlalchemy import String, ForeignKey, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Memory(Base):
    __tablename__ = 'memories'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    book_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("memory_books.id"), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    mood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    happened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now ,onupdate=datetime.now)

    """给content添加全文索引"""
    __table_args__ = (
        Index("ft_content_mood_location", "content", "mood", "location",
              mysql_prefix="FULLTEXT", mysql_with_parser="ngram"),
    )