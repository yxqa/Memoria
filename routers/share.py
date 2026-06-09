from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from core.deps import get_current_user
from core.ption_handlers import AppException
from crud.share import create_share_link, get_shared_memory
from models import User
from schemas import ShareCreate

# 需要鉴权的接口（在 memories router 下）
memories_share_router = APIRouter()

@memories_share_router.post("/{memory_id}/share")
async def create_share(
        memory_id: str,
        data: ShareCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    status, share = await create_share_link(
        db, current_user.id, memory_id,
        expire_hours=data.expire_hours or 24,
        password=data.password
    )
    if status == "MEMORY_NOT_FOUND":
        raise AppException(404, "记忆不存在", "MEMORY_NOT_FOUND")

    share_url = f"/s/{share.token}"
    return {
        "share_id": share.id,
        "share_url": share_url,
        "token": share.token,
        "expire_at": share.expire_at.isoformat(),
        "has_password": share.password_hash is not None,
        "created_at": share.created_at.isoformat(),
    }


# 公开接口（不需要鉴权，挂在根路径）
public_router = APIRouter()

@public_router.get("/s/{token}")
async def access_share(
        token: str,
        password: str | None = Query(None),
        db: AsyncSession = Depends(get_db)
):
    status, data = await get_shared_memory(db, token, password)

    if status == "SHARE_NOT_FOUND":
        raise AppException(404, "分享链接不存在", "SHARE_NOT_FOUND")
    if status == "SHARE_EXPIRED":
        raise AppException(410, "分享链接已过期", "SHARE_EXPIRED")
    if status == "SHARE_PASSWORD_REQUIRED":
        raise AppException(401, "需要访问密码", "SHARE_PASSWORD_REQUIRED")
    if status == "INVALID_PASSWORD":
        raise AppException(401, "密码错误", "INVALID_PASSWORD")

    return data