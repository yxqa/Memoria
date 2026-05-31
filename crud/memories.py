import json
import os
import uuid

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Memory, Tag, MemoryTag, MediaFile
from models.media_files import FileType
from schemas import MemoryCreate


ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg",".webp"}   #图片类型
ALLOWED_VIDEO_EXT = {".mp4",".webm"}                    #视频格式
MAX_IMAGE_SIZE = 10 * 1024 * 1024                       #图片最大大小
MAX_VIDEO_SIZE = 100 * 1024 * 1024                      #视频最大大小
MAX_IMAGE_COUNT = 9                                     #图片数量
UPLOAD_BASE = "uploads"



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
        tag_names = json.loads(memoria_data.tags)
        for tag_name in tag_names:
            result = await db.execute(
                select(Tag).where(
                    Tag.user_id == user_id,
                    Tag.name == tag_name
                )
            )
            existing = result.scalar_one_or_none()

            if existing is None:
                new_tag = Tag(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    name=tag_name,
                )
                db.add(new_tag)
                await db.flush()
                tag_id = new_tag.id
            else:
                tag_id = existing.id

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