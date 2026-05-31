from os.path import basename

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from core.deps import get_current_user
from crud.memories import create_new_memoria
from models import User, Tag, MemoryTag, MediaFile
from schemas import MemoryCreate, MemoryUpdate, TagSyncRequest, MemoryCreateResponse

router = APIRouter(prefix="/memories",tags=["memories"])


@router.post("", response_model=MemoryCreateResponse)
async def create_memoria(
        memoria_data: MemoryCreate = Depends(),
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
    result_tags = await db.execute(
        select(Tag.name)
        .join(MemoryTag, MemoryTag.tag_id == Tag.id)
        .where(MemoryTag.memory_id == memoria.id)
    )
    tags = result_tags.scalars().all()

    # 2. 查询媒体文件
    result_media = await db.execute(
        select(MediaFile)
        .where(MediaFile.memory_id == memoria.id)
        .order_by(MediaFile.upload_order)
    )
    media = result_media.scalars().all()

    images = []
    videos = None

    for med in media:
        if med.file_type == "image":
            images.append({
                "id": med.id,
                "url": f"/api/v1/media/{basename(med.file_path)}",
                "upload_order": med.upload_order,
            })
        if med.file_type == "video":
            videos = {
                "id": med.id,
                "url": f"/api/v1/media/{basename(med.file_path)}",
                "upload_order": med.upload_order,
                "file_size": med.file_size
            }

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
async def get_memoria(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    查询记忆列表
    :param current_user: 当前用户
    :param db: 数据库
    :return:
    """

    pass

@router.get("/{memories_id}")
async def get_one_memoria(
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
    pass

@router.put("/{memories_id}")
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

    pass

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
    pass

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

    pass