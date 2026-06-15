from fastapi import APIRouter, Depends

from core.deps import get_current_user
from models import User

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("")
async def get_tags_all(
        current_user: User = Depends(get_current_user),
):
    """获取当前用户所有标签及其使用次数"""
    pass