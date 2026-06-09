import hashlib
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.memories import get_tags, get_media
from models import Memory, ShareLink, User, Tag, MemoryTag, MediaFile


def _hash_password(password: str) -> str:
    """SHA-256 简单哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

async def create_share_link(
        db: AsyncSession,
        user_id: str,
        memory_id: str,
        expire_hours: int = 24,
        password: str | None = None,
):
    #校验记忆归属
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == user_id,
        )
    )

    if not result.scalar_one_or_none():
        return "MEMORY_NOT_FOUND", None

    token = uuid.uuid4().hex + uuid.uuid4().hex
    expire_at = datetime.now() + timedelta(hours=expire_hours)

    share = ShareLink(
        id = str(uuid.uuid4()),
        memory_id = memory_id,
        user_id = user_id,
        token = token,
        password_hash = _hash_password(password) if password else None,
        expire_at = expire_at,
    )

    db.add(share)
    await db.commit()
    await db.refresh(share)
    return "OK", share

async def get_shared_memory(
        db: AsyncSession,
        token: str,
        password: str | None = None,
):
    result = await db.execute(
        select(ShareLink).where(ShareLink.token == token)
    )
    share = result.scalar_one_or_none()
    if not share:
        return "MEMORY_NOT_FOUND", None
    if share.expire_at < datetime.now():
        return "MEMORY_EXPIRED", None
    if share.password_hash:
        if not password:
            return "SHARE_PASSWORD_REQUIRED", None
        if _hash_password(password) != share.password_hash:
            return "INVALID_PASSWORD", None

    #查记忆
    result_memory = await db.execute(
        select(Memory).where(Memory.id == share.memory_id)
    )
    memory = result_memory.scalar_one_or_none()
    if not memory:
        return "SHARE_NOT_FOUND", None

    #查看分享者用户名
    result_user = await db.execute(
        select(User).where(User.id == share.user_id)
    )
    user = result_user.scalar_one_or_none()

    #查标签
    tags = await get_tags(db, memory.id)

    #查媒体
    images, video = await get_media(db, memory.id)

    #更新访问次数
    share.view_count += 1
    await db.commit()

    return "OK",{
        "memory":{
            "id": memory.id,
            "content": memory.content,
            "mood": memory.mood,
            "location": memory.location,
            "happened_at": memory.happened_at.isoformat() if memory.happened_at else None,
            "tags": list(tags),
        },
        "images": images,
        "video": video,
        "shared_by": {"username": user.username if user else ""},
        "expire_at": share.expire_at.isoformat(),
    }