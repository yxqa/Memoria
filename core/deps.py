from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from core.security import decode_token
from models import User

# FastAPI内置工具，自动从请求头提取Bearer token
security_schema = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security_schema),
        db: AsyncSession = Depends(get_db)
) -> User:
    """
    从Authorization请求头中解析token -> 提取 user_id -> 查库 -> 返回User对象
    :param credentials:
    :param db:
    :return:
    """

    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Token中缺少用户标识"
        )

    #查数据库
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user