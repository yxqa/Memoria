import os
import uuid
from datetime import date
from os.path import basename

from fastapi import UploadFile
from sqlalchemy import select, or_, and_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import Memory, Tag, MemoryTag, MediaFile, MemoryBook
from models.media_files import FileType
from schemas import MemoryCreate, MemoryUpdate

ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg",".webp"}   #图片类型
ALLOWED_VIDEO_EXT = {".mp4",".webm"}                    #视频格式
MAX_IMAGE_SIZE = 10 * 1024 * 1024                       #图片最大大小
MAX_VIDEO_SIZE = 100 * 1024 * 1024                      #视频最大大小
MAX_IMAGE_COUNT = 9                                     #图片数量
UPLOAD_BASE = "uploads"



async def _get_or_create_tag(db: AsyncSession, user_id: str, tag: str) -> str:
    """查找已有标签，若不存在则创建标签，返回tag_id"""

    result = await db.execute(
        select(Tag)
        .where(Tag.user_id == user_id, Tag.name == tag)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing.id

    new_tag = Tag(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=tag,
    )
    db.add(new_tag)
    await db.flush()
    return new_tag.id

async def get_all_memoria(
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        book_id: str | None = None,
        tag: str | None= None,
        mood: str | None= None,
        q: str | None= None,
        start: date = None,
        end: date = None,
):


    offset = (page - 1) * page_size

    #构建过滤条件
    conditions = [Memory.user_id == user_id]
    if book_id:
        conditions.append(Memory.book_id == book_id)

    if mood:
        conditions.append(Memory.mood == mood)

    if q:
        #全文搜索，对content、mood、location做LIKE模糊匹配
        conditions.append(
            or_(
                Memory.content.like(f"%{q}%"),
                Memory.mood.like(f"%{q}%"),
                Memory.location.like(f"%{q}%")
            )
        )

    if start:
        conditions.append(Memory.created_at >= start)
    if end:
        # end当天结束，+1天变成<, 覆盖当天全天
        from datetime import timedelta
        conditions.append(Memory.created_at < (end + timedelta(days=1)))

    # 构建select对象
    query = select(Memory).where(and_(*conditions))
    count_query = select(func.count()).select_from(Memory).where(and_(*conditions))

    if tag:
        # tag过滤需要join memory_tag和tags
        query = (
            query
            .join(MemoryTag, MemoryTag.memory_id == Memory.id)
            .join(Tag, Tag.id == MemoryTag.tag_id)
            .where(Tag.name == tag)
            .where(Tag.user_id == user_id)
        )

        count_query = (
            select(func.count(Memory.id.distinct())).select_from(Memory).where(and_(*conditions))
            .join(MemoryTag, MemoryTag.memory_id == Memory.id)
            .join(Tag, Tag.id == MemoryTag.tag_id)
            .where(Tag.name == tag)
            .where(Tag.user_id == user_id)
        )

    #查总数
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    #查列表
    result = await db.execute(
        query
        .order_by(Memory.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    memories = result.scalars().all()

    if not memories:
        return [], total

    memory_ids = [m.id for m in memories]

    #批量查标签
    tag_result = await db.execute(
        select(MemoryTag.memory_id, Tag.name)
        .join(Tag, Tag.id == MemoryTag.tag_id)
        .where(MemoryTag.memory_id.in_(memory_ids))
    )

    tags_map: dict[str, list[str]] = {}
    for memory_id, tag_name in tag_result.all():
        tags_map.setdefault(memory_id, []).append(tag_name)

    #批量查媒体统计
    media_result = await db.execute(
        select(MediaFile.memory_id, MediaFile.file_type)
        .where(MediaFile.memory_id.in_(memory_ids))
    )

    image_count_map: dict[str, int] = {}
    has_video_map: dict[str, bool] = {}

    for memory_id, file_type in media_result.all():
        if file_type == FileType.IMAGE:
            image_count_map[memory_id] = image_count_map.get(memory_id, 0) + 1
        elif file_type == FileType.VIDEO:
            has_video_map[memory_id] = True

    #组装
    items = []
    for m in memories:
        items.append({
            "id": m.id,
            "content": m.content,
            "mood": m.mood,
            "location": m.location,
            "happened_at": m.happened_at.isoformat() if m.happened_at else None,
            "book_id": m.book_id,
            "tags": tags_map.get(m.id, []),
            "image_count": image_count_map.get(m.id, 0),
            "has_video": has_video_map.get(m.id, False),
            "created_at": m.created_at.isoformat()
        })
    return items, total

async def create_new_memoria(
        db: AsyncSession,
        memoria_data: MemoryCreate,
        user_id: str,
        images: list[UploadFile] | None = None,
        video: UploadFile | None = None
):
    # 0. 基本校验：content/images/video 至少提供一项
    if not memoria_data.content and not images and not video:
        raise ValueError("content、images、video 至少提供一项")

    # 1. 创建记忆主体
    memoria = Memory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        book_id=memoria_data.book_id,
        content=memoria_data.content,
        mood=memoria_data.mood,
        location=memoria_data.location,
        happened_at=memoria_data.happened_at
    )
    db.add(memoria)
    await db.flush()

    # 2. 处理标签
    if memoria_data.tags:
        for tag_name in memoria_data.tags:

            tag_id = await _get_or_create_tag(db, user_id, tag_name)
            db.add(MemoryTag(
                memory_id=memoria.id,
                tag_id=tag_id
            ))

    # 3. 处理视频/图片文件
    upload_files = []
    # 3a. 校验图片
    images = images or []
    if len(images) > MAX_IMAGE_COUNT:
        raise ValueError(f"图片最多{MAX_IMAGE_COUNT}张")

    for img in images:
        ext = os.path.splitext(img.filename)[1].lower()
        if ext not in ALLOWED_IMAGE_EXT:
            raise ValueError(f"不支持的图片类型:{ext}")
        if img.size > MAX_IMAGE_SIZE:
            raise ValueError(f"图片{img.filename}大小超过10MB")

    # 3b. 校验视频
    if video:
        ext = os.path.splitext(video.filename)[1].lower()
        if ext not in ALLOWED_VIDEO_EXT:
            raise ValueError(f"不支持的视频类型:{ext}")
        if video.size > MAX_VIDEO_SIZE:
            raise ValueError(f"视频{video.filename}大小超过100MB")

    # 3c. 键目录(本地保存)
    memory_dir = os.path.join(UPLOAD_BASE, user_id, memoria.id)
    os.makedirs(memory_dir, exist_ok=True)

    # 3d. 保存图片
    for order, img in enumerate(images):
        ext = os.path.splitext(img.filename)[1].lower()
        file_uuid = str(uuid.uuid4())
        file_path = os.path.join(memory_dir, f"{file_uuid}{ext}")

        content = await img.read()
        with open(file_path, "wb") as f:
            f.write(content)

        db.add(MediaFile(
            id=file_uuid,
            memory_id=memoria.id,
            user_id=user_id,
            file_type=FileType.IMAGE,
            file_path=file_path,
            file_size=len(content),
            upload_order=order
        ))
        upload_files.append(file_uuid)

    # 3e. 保存视频
    if video:
        ext = os.path.splitext(video.filename)[1].lower()
        file_uuid = str(uuid.uuid4())
        file_path = os.path.join(memory_dir, f"{file_uuid}{ext}")

        content = await video.read()
        with open(file_path, "wb") as f:
            f.write(content)

        db.add(MediaFile(
            id=file_uuid,
            memory_id=memoria.id,
            user_id=user_id,
            file_type=FileType.VIDEO,
            file_path=file_path,
            file_size=len(content),
            upload_order=0
        ))
        upload_files.append(file_uuid)

    await db.commit()
    await db.refresh(memoria)
    return memoria, upload_files

async def get_tags(db: AsyncSession, memoria_id):
    result_tags = await db.execute(
        select(Tag.name)
        .join(MemoryTag, MemoryTag.tag_id == Tag.id)
        .where(MemoryTag.memory_id == memoria_id)
    )
    tags = result_tags.scalars().all()
    return tags

async def get_media(db: AsyncSession, memoria_id):
    result_media = await db.execute(
        select(MediaFile)
        .where(MediaFile.memory_id == memoria_id)
        .order_by(MediaFile.upload_order)
    )
    media = result_media.scalars().all()

    images = []
    video = None

    for med in media:
        if med.file_type == "image":
            images.append({
                "id": med.id,
                "url": f"/api/v1/media/{basename(med.file_path)}",
                "upload_order": med.upload_order,
            })
        elif med.file_type == "video":
            video = {
                "id": med.id,
                "url": f"/api/v1/media/{basename(med.file_path)}",
                "upload_order": med.upload_order,
                "file_size": med.file_size
            }


    return images, video

async def get_one_memoria(db: AsyncSession, user_id, memoria_id):

    # 记忆信息
    #outerjoin: 外连接
    result_memoria = await db.execute(
        select(Memory, MemoryBook.title.label("book_title"))
        .outerjoin(MemoryBook, MemoryBook.id == Memory.book_id)
        .where(Memory.user_id == user_id, Memory.id == memoria_id)
    )
    row = result_memoria.one_or_none()

    if not row:
        return None
    memoria, book_title = row

    # 标签信息
    result_tags = await get_tags(db, memoria_id)

    # 媒体信息
    result_images, result_video = await get_media(db, memoria_id)

    return {
        "id": memoria_id,
        "content": memoria.content,
        "mood": memoria.mood,
        "location": memoria.location,
        "happened_at": memoria.happened_at,
        "book_id": memoria.book_id,
        "book_title": book_title,
        "tags": result_tags,
        "images": result_images,
        "video": result_video,
        "created_at": memoria.created_at,
        "updated_at": memoria.updated_at,
    }

async def update_new_memoria(
        db: AsyncSession,
        user_id: str,
        memoria_id: str,
        memoria_data: MemoryUpdate
):

    result = await db.execute(select(Memory).where(Memory.id == memoria_id, Memory.user_id == user_id))
    memoria = result.scalar_one_or_none()
    if not memoria:
        return None

    if memoria_data.content is not None:
        memoria.content = memoria_data.content
    if memoria_data.mood is not None:
        memoria.mood = memoria_data.mood
    if memoria_data.location is not None:
        memoria.location = memoria_data.location
    if memoria_data.happened_at is not None:
        memoria.happened_at = memoria_data.happened_at

    #判断book_id是否传入
    #model_fields_set: 一个集合，记录那些对象被显式的设置过
    #用于区分 【显式设置为None】和【从未设置】两种情况
    if "book_id" in memoria_data.model_fields_set:
        memoria.book_id = memoria_data.book_id if memoria_data.book_id else None

    #标签: 全量替换
    if memoria_data.tags is not None:

        #删除该记忆里的全部标签
        await db.execute(
            delete(MemoryTag)
            .where(MemoryTag.memory_id == memoria_id)
        )

        #重新添加标签
        for tag in memoria_data.tags:
            tag_id = await _get_or_create_tag(db, user_id, tag)
            db.add(MemoryTag(memory_id=memoria_id, tag_id=tag_id))

    await db.commit()
    await db.refresh(memoria)

    images, video = await get_media(db, memoria_id)

    return {
        "id": memoria.id,
        "content": memoria.content,
        "mood": memoria.mood,
        "location": memoria.location,
        "happened_at": memoria.happened_at,
        "book_id": memoria.book_id,
        "tags": await get_tags(db, memoria_id),
        "images": images,
        "video": video,
        "created_at": memoria.created_at,
        "updated_at": memoria.updated_at,
    }

async def delete_memoria_by_userid(db: AsyncSession, user_id: str, memoria_id: str):

    """
        优先删除无任何额外引用的表,最后删除主表。顺序为
        1. 删除标签信息
        2. 删除媒体文件
        3. 删除记忆
    """
    #确认记忆存在
    result = await db.execute(
        select(Memory)
        .where(Memory.id == memoria_id, Memory.user_id == user_id)
    )

    #删除标签关联
    await db.execute(
        delete(MemoryTag)
        .where(MemoryTag.memory_id == memoria_id)
    )

    #删除媒体文件
    await db.execute(
        delete(MediaFile)
        .where(MediaFile.memory_id == memoria_id, MediaFile.user_id == user_id)
    )

    #删除记忆.
    #需要首先验证记忆存在
    memoria = result.scalar_one_or_none()
    if not memoria:
        return False

    await db.execute(
        delete(Memory)
        .where(Memory.id == memoria_id, Memory.user_id == user_id)
    )
    await db.commit()
    return True

async def delete_tag(db: AsyncSession, user_id: str, memoria_id: str, tag_id: str):

    """
        删除标签流程
        1.
          - 记忆存在 and 属于当前用户
          - 标签存在 and 属于当前用户
          - 确认标签属于这条记忆
        2. 删除标签
        3. 返回结果
    """

    #判断记忆存在
    result_memoria = await db.execute(
        select(Memory)
        .where(Memory.id == memoria_id, Memory.user_id == user_id)
    )
    if not result_memoria.scalar_one_or_none():
        return "MEMORY_NOT_FOUND"

    #判断标签是否存在
    result_tag = await db.execute(
        select(Tag)
        .where(Tag.user_id == user_id, Tag.id == tag_id)
    )
    if not result_tag.scalar_one_or_none():
        return "TAG_NOT_FOUND"

    #确认标签属于这条记忆
    result_bind = await db.execute(
        select(MemoryTag)
        .where(MemoryTag.memory_id == memoria_id, MemoryTag.tag_id == tag_id)
    )
    if not result_bind.scalar_one_or_none():
        return "TAG_NOT_FOUND"

    #删除标签
    await db.execute(
        delete(MemoryTag)
        .where(MemoryTag.memory_id == memoria_id, MemoryTag.tag_id == tag_id)
    )
    await db.commit()
    return "SUCCESS"



