import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core import security
from models import User
from schemas import UserCreate


#查询用户
async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


#创建用户
async def create_user(db: AsyncSession, user_data: UserCreate):
    #密码加密
    hash_pwd = security.hash_password(user_data.password)
    user = User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        password_hash=hash_pwd)
    db.add(user)
    await db.commit()
    await db.refresh(user)      #从数据库中读取最新的user
    return user

#登录校验
async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify_password(password, user.password_hash):
        return None
    return user