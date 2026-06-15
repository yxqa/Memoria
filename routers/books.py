from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from core.deps import get_current_user
from core.ption_handlers import AppException
from crud.memorybook import create_book, get_book_by_user_and_title, get_book, memory_counts, update_memory_book, \
    delete_memory_book
from models import User
from schemas import BookCreate, BookUpdate

router = APIRouter(prefix="/books", tags=["books"])



@router.post("", status_code=201)
async def memory_book(
        memory_data: BookCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    添加记忆本
    :param memory_data: 记忆本对象
    :param current_user:
    :param db:
    :return:
    """
    existing_book = await get_book_by_user_and_title(db, current_user.id, memory_data.title)
    if existing_book:
        raise AppException(status_code=409, detail="记忆本名重复，请修改", code="BOOK_TITLE_EXISTS")

    result = await create_book(current_user.id, memory_data, db)
    return {
      "id": result.id,
      "title": result.title,
      "cover_image": result.cover_image,
      "sort_order": result.sort_order,
      "memory_count": 0,
      "created_at":result.created_at
    }


@router.get("")
async def get_memory_books(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    item = []
    result = await get_book(db, current_user.id)
    for book in result:
        item.append({
            "id": book.id,
            "title": book.title,
            "cover_image": book.cover_image,
            "sort_order": book.sort_order,
            "memory_count": await memory_counts(db, book.id),
            "created_at": book.created_at.isoformat()
        })
    return {"items": item}

@router.patch("/{book_id}")
async def update_book(
        book_id: str,
        book_data: BookUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    result = await update_memory_book(db,book_id, current_user.id, book_data)

    if not result:
        raise AppException(status_code=404, detail="记忆本不存在", code="BOOK_NOT_FOUND")

    return {
      "id": result.id,
      "title": result.title,
      "cover_image": result.cover_image,
      "sort_order": result.sort_order,
      "memory_count": 0,
      "created_at": result.created_at
    }

@router.delete("/{book_id}")
async def delete_book(
        book_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await delete_memory_book(db, book_id, current_user.id)
    if not result:
        raise AppException(status_code=404, detail="记忆本不存在", code="BOOK_NOT_FOUND")
    return {"message": f"{book_id} 删除成功"}




