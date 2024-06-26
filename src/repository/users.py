from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    statement = select(User).filter_by(email=email)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema | dict, db: AsyncSession = Depends(get_db), avatar=None):
    new_user = None
    if not avatar:
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as err:
            print(err)
    if isinstance(body, UserSchema):
        new_user = User(**body.model_dump(), avatar=avatar)
    elif isinstance(body, dict):
        new_user = User(**body, avatar=avatar)
    if new_user:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()
