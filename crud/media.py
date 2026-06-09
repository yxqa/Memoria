from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import MediaFile


async def get_media_file(db: AsyncSession, userid: str, filename: str):
    file_id = filename.rsplit(".", 1)[0]
    result = await db.execute(
        select(MediaFile).where(MediaFile.id == file_id)
    )
    media = result.scalar_one_or_none()
    if not media:
        return "FILE NOT FOUND", None
    if media.id != userid:
        return "FORBIDDEN", None
    return "OK", media