import uuid
from datetime import datetime

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import MemoryBook, Memory
from schemas import BookCreate, BookUpdate


async def get_book_by_user_and_title(db: AsyncSession,user_id, title):
    result = await db.execute(select(MemoryBook).where(MemoryBook.user_id == user_id, MemoryBook.title == title))
    return result.scalar_one_or_none()


async def get_book(db: AsyncSession, user_id):
    result = await db.execute(select(MemoryBook).where(MemoryBook.user_id == user_id))
    return result.scalars().all()

async def create_book(
        user_id: str,
        memory_data: BookCreate,
        db: AsyncSession
):
    """
    创建记忆本
    :param memory_data:
    :param user_id:
    :param db:
    :return:
    """
    book = MemoryBook(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=memory_data.title,
        cover_image=memory_data.cover_image,
        sort_order=memory_data.sort_order
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book

async def memory_counts(db: AsyncSession, book_id):
    result = await db.execute(select(func.count(Memory.book_id)).where(Memory.book_id == book_id))
    return result.scalar()


async def update_memory_book(
        db: AsyncSession,
        book_id: str,
        user_id: str,
        book_data: BookUpdate,
):

    #1. 查询库
    result = await db.execute(select(MemoryBook).where(MemoryBook.id == book_id, MemoryBook.user_id == user_id))
    book = result.scalar_one_or_none()
    if not book:
        return None

    #2. 更新
    if book_data.title is not None:
        book.title = book_data.title
    if book_data.cover_image is not None:
        book.cover_image = book_data.cover_image
    if book_data.sort_order is not None:
        book.sort_order = book_data.sort_order
    book.updated_at = datetime.now()

    await db.commit()
    await db.refresh(book)
    return book

async def delete_memory_book(db: AsyncSession, book_id: str, user_id: str):

    result = await db.execute(select(MemoryBook).where(MemoryBook.id == book_id, MemoryBook.user_id == user_id))
    book = result.scalar_one_or_none()
    if not book:
        return None

    await db.execute(update(Memory)
                     .where(Memory.book_id == book_id, Memory.user_id == user_id)
                     .values(book_id=None))
    await db.delete(book)
    await db.commit()
    return True
