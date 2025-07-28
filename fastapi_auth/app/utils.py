from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_auth.app.auth.models import User
from fastapi_auth.app.database import async_db


async def get_user_db(
    session: AsyncSession = Depends(async_db.get_async_session),
):
    yield SQLAlchemyUserDatabase(session, User)
