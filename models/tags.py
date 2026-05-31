from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)