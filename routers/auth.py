from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from core.deps import get_current_user
from core.ption_handlers import AppException
from core.security import create_refresh_token, create_access_token
from models import User, MemoryBook
from schemas import UserCreate, UserLogin
from crud.users import get_user_by_username, create_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register_user(user_data: UserCreate ,db: AsyncSession = Depends(get_db)):
    """
    用户注册
    :return:
    """

    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise AppException(status_code=409, detail="用户已存在", code="USERNAME_EXISTS")

    user = await create_user(db, user_data)
    return {
      "id":user.id,
      "username": user.username,
      "created_at": user.created_at.isoformat()
    }


@router.post("/login")
async def login_user(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    用户登录
    :param user_data:
    :param db:
    :return:
    """
    # 1. 查用户
    # 2. 校验密码
    user = await authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在或者密码错误")

    # 3. 生成 access_token + refresh_token
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    # 4. 返回 TokenResponse
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_at": 3600
    }

@router.post("/refresh")
async def update_refresh_token(refresh_token, db: AsyncSession = Depends(get_db)):
    pass

@router.get("/me")
async def get_user(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 记忆总数
    memory_count_result = await db.execute(
        select(func.count(MemoryBook.id)).where(MemoryBook.user_id == current_user.id)
    )
    memory_count = memory_count_result.scalar()

    #记忆本总数
    book_count_result = await db.execute(
        select(func.count(MemoryBook.id)).where(MemoryBook.user_id == current_user.id)
    )
    book_count = book_count_result.scalar()

    return {
      "id": current_user.id,
      "username": current_user.username,
      "is_active": current_user.is_active,
      "memory_count": memory_count,
      "book_count": book_count,
      "created_at": current_user.created_at.isoformat(),
    }

@router.patch("/me")
async def update_user_pwd(old_pwd: str, new_pwd: str, db: AsyncSession = Depends(get_db)):
    pass