import pandas as pd
import pickle
import redis.asyncio as redis

from fastapi_missing.app.settings import settings
from fastapi_missing.app.exceptions import DataNotFound

class RedisConnection:
    redis = None

    @classmethod
    async def connect(cls):
        if cls.redis is None:
            cls.redis = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        try:
            await cls.redis.ping()
        except Exception as error:
            print(f"Неудачная попытка подключиться к Redis: {error}")

    @classmethod
    async def disconnect(cls):
        if redis is not None:
            try:
                await cls.redis.aclose()
            except Exception as error:
                print(f"Произошла ошибка при разрыве соединения с Redis: {error}")

    @classmethod
    async def set_dataframe(
        cls, 
        user_id: str, 
        df: pd.DataFrame, 
        key_suffix: str = "", 
        file_id: int | None = None
    ) -> None:
        """Сохраняет DataFrame в Redis с возможностью добавления суффикса к ключу."""
        key = f"{user_id}_data{key_suffix}"
        await cls.redis.set(key, pickle.dumps(df))
        
        if file_id is not None:
            await cls.redis.set(f"{user_id}_file_id", pickle.dumps(file_id))

    @classmethod
    async def get_dataframe(
        cls, 
        user_id: str, 
        key_suffix: str = ""
    ) -> pd.DataFrame:
        """Получает DataFrame из Redis по ключу с суффиксом."""
        key = f"{user_id}_data{key_suffix}"
        data = await cls.redis.get(key)
        
        if data is None:
            raise DataNotFound(f"Данные не найдены для ключа: {key}")
        return pickle.loads(data)
