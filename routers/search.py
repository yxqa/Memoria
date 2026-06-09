from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from core.deps import get_current_user
from crud.search import get_search_memoria
from models import User

router = APIRouter(prefix="/search", tags=["search"])

@router.get("")
async def get_search(
        q: str,
        page: int = 1,
        page_size: int = 20,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),

):
    user_id = current_user.id
    result = await get_search_memoria(db, user_id, q, page, page_size)
    return result