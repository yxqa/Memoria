import mimetypes
import os.path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from config.db_config import get_db
from core.deps import get_current_user
from core.ption_handlers import AppException
from crud.media import get_media_file
from models import User

router = APIRouter(prefix="media", tags=["media"])


@router.get("{filename}")
async def read_file(
        filename: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    status, media = await get_media_file(db, user_id, filename)
    if status == "FILE NOT FOUND":
        raise AppException(status_code=404, detail="文件不存在", code="FILE_NOT_FOUND")
    if status == "FORBIDDEN":
        raise AppException(status_code=403, detail="无权访问", code="FORBIDDEN")

    #校验磁盘文件是否存在
    if not os.path.exists(media.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    #自动识别Content-Type
    content_type, _ = mimetypes.guess_type(filename)
    content_type = content_type or "application/octet-stream"

    return FileResponse(
        path=media.file_path,
        media_type=content_type,
        filename=filename,
    )

