from datetime import date

from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from core.deps import get_current_user
from core.ption_handlers import AppException
from crud.memories import create_new_memoria, get_all_memoria, get_tags, get_media, get_one_memoria, update_new_memoria, \
    delete_memoria_by_userid, delete_tag
from models import User
from schemas import MemoryCreate, MemoryUpdate, TagSyncRequest, MemoryCreateResponse

router = APIRouter(prefix="/memories",tags=["memories"])


@router.post("", response_model=MemoryCreateResponse)
async def create_memoria(
        memoria_data: MemoryCreate = Depends(MemoryCreate.as_form),
        image: list[UploadFile] | None = File(None),
        video: UploadFile | None = File(None),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    创建记忆

    - 支持文本, 心情, 标签
    - 可选关联到某个记忆本中

    :param image:
    :param video:
    :param memoria_data: 用户传入的请求数据
    :param current_user: 当前用户
    :param db: 数据库
    :return:
    """
    memoria, uploaded_files = await create_new_memoria(db, memoria_data, current_user.id, image, video)

    # 1. 查询标签列表
    tags = await get_tags(db,memoria.id)

    # 2. 查询媒体文件
    images, videos = await get_media(db,memoria.id)

    return {
      "id": memoria.id,
      "content": memoria.content,
      "mood": memoria.mood,
      "location": memoria.location,
      "happened_at": memoria.happened_at.isoformat() if memoria.happened_at else None,
      "book_id": memoria.book_id,
      "tags": tags,
      "images": images,
      "video": videos,
      "created_at": memoria.created_at.isoformat(),
      "updated_at": memoria.updated_at.isoformat(),
    }

@router.get("")
async def get_memories(
        page: int = Query(1,ge=1),
        page_size: int = Query(20, ge=1, le=100),
        book_id: str | None = Query(None, description="按照记忆本过滤"),
        tag: str | None = Query(None, description="按标签过滤"),
        mood: str | None = Query(None, description="按心情过滤"),
        q: str | None = Query(None, description="全文搜索关键词"),
        start_date: date | None = Query(None, description="开始时间"),
        end_date: date | None = Query(None, description="结束时间"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    查询记忆列表
    :param page:
    :param page_size:
    :param book_id:
    :param tag:
    :param mood:
    :param q:
    :param end_date:
    :param start_date:
    :param current_user: 当前用户
    :param db: 数据库
    :return:
    """
    result, total = await get_all_memoria(
        db,
        current_user.id,
        page,
        page_size,
        book_id,
        tag,
        mood,
        q,
        start_date,
        end_date
    )

    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_page": (total + page_size - 1) // page_size
    }

@router.get("/{memories_id}")
async def get_memoria(
        memories_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    获取单条记忆详情(含所有媒体文件)

    :param memories_id: UUID
    :param current_user: 当前用户
    :param db: 数据库
    :return:
    """
    result = await get_one_memoria(db, current_user.id, memories_id)
    if not result:
        raise AppException(status_code=404, detail="不存在记忆",code="MEMORY_NOT_FOUND")
    return result

@router.post("/{memories_id}")
async def update_memoria(
        memories_id: str,
        memoria_data: MemoryUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    更新记忆的文字, 心情, 位置, 标签等等。
    不支持更新媒体文件(需要先删除后重新上传)

    :param memoria_data: 更新信息
    :param memories_id: 记忆UUID
    :param current_user: 当前用户
    :param db: 数据库
    :return:
    """
    user_id = current_user.id
    result = await update_new_memoria(db, user_id, memories_id, memoria_data)
    if not result:
        AppException(status_code=404, detail="该记忆不存在", code="MEMORY_NOT_FOUND")
    return result

@router.delete("/{memories_id}")
async def delete_memoria(
        memories_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    删除记忆及其关联的媒体文件
    :param memories_id: 记忆UUID
    :param current_user: 当前用户
    :param db: 数据库
    :return:
    """
    user_id = current_user.id
    result = await delete_memoria_by_userid(db, user_id, memories_id)

    if not result:
        raise AppException(status_code=404, detail="记忆不存在", code="MEMORY_NOT_FOUND")
    return {"message": "记忆已删除"}

@router.post("/{memories_id}/tags")
async def update_memoria_tags(
        memories_id: str,
        tags: TagSyncRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    同步标签(全量替换)
    :param tags: 标签名列表
    :param memories_id: 记忆UUID
    :param current_user: 当前用户
    :param db: 数据库
    :return:
    """
    pass

@router.delete("/{memories_id}/tags/{tag_id}")
async def delete_memoria_tags(
        memories_id: str,
        tag_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    移除单个标签
    :param memories_id:记忆UUID
    :param tag_id:标签UUID
    :param current_user: 当前用户
    :param db: 数据库
    :return:
    """
    user_id = current_user.id
    result = await delete_tag(db, user_id, memories_id, tag_id)
    if result == "MEMORY_NOT_FOUND":
        raise AppException(status_code=404, detail="记忆不存在", code="MEMORY_NOT_FOUND")
    if result == "TAG_NOT_FOUND":
        raise AppException(status_code=404, detail="标签不存在或者该记忆没有该标签", code="TAG_NOT_FOUND")
    return {"message": "标签已移除"}