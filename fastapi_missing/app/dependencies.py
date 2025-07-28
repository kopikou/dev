from fastapi import Security, HTTPException,Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fastapi_missing.app.requests import get_user_uuid
from fastapi_missing.app.memory import RedisConnection
from typing import Optional

security = HTTPBearer()

async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    return credentials.credentials

async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    token = credentials.credentials
    return await get_user_uuid(user_token=token)

async def get_user_data(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    user_id = await get_current_user_uuid(credentials=credentials)
    df = await RedisConnection.get_dataframe(user_id=user_id)
    return {"user_id": user_id, "data": df}

async def get_user_data_with_original(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Получает данные пользователя, сохраняя оригинальные данные."""
    user_id = await get_current_user_uuid(credentials=credentials)
    
    file_id = request.query_params.get("file_id")
    if not file_id:
        raise HTTPException(status_code=400, detail="File ID is required")
    
    df = await RedisConnection.get_dataframe(user_id=user_id)
    
    return {
        "user_id": user_id,
        "data": df.copy(),  # Рабочая копия
        "original_data": df.copy()  # Сохраняем оригинал
    }