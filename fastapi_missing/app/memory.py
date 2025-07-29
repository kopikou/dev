import pandas as pd
import pickle
from pathlib import Path
from fastapi_missing.app.settings import settings
from fastapi_missing.app.exceptions import DataNotFound

class LocalStorage:
    @staticmethod
    def _get_user_dir(user_id: str) -> Path:
        """Создает папку для хранения данных пользователя"""
        user_dir = Path(settings.storage_dir) / "user_data" / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    @classmethod
    async def set_dataframe(
        cls, 
        user_id: str, 
        df: pd.DataFrame, 
        key_suffix: str = "", 
        file_id: int | None = None
    ) -> None:
        """Сохраняет DataFrame в файл с возможностью добавления суффикса к имени файла."""
        user_dir = cls._get_user_dir(user_id)
        
        # Сохраняем DataFrame с учетом суффикса
        filename = f"data{key_suffix}.pkl"
        df.to_pickle(user_dir / filename)
        
        if file_id is not None:
            with open(user_dir / "file_id.pkl", "wb") as f:
                pickle.dump(file_id, f)

    @classmethod
    async def get_dataframe(
        cls, 
        user_id: str, 
        key_suffix: str = ""
    ) -> pd.DataFrame:
        """Получает DataFrame из файла по суффиксу."""
        user_dir = cls._get_user_dir(user_id)
        filename = f"data{key_suffix}.pkl"
        data_path = user_dir / filename
        
        if not data_path.exists():
            raise DataNotFound(f"Data not found for user {user_id} with suffix {key_suffix}")
            
        return pd.read_pickle(data_path)

    @classmethod
    async def set_file_id(cls, user_id: str, file_id: int):
        user_dir = cls._get_user_dir(user_id)
        with open(user_dir / "file_id.pkl", "wb") as f:
            pickle.dump(file_id, f)

    @classmethod
    async def get_file_id(cls, user_id: str) -> int:
        user_dir = cls._get_user_dir(user_id)
        file_id_path = user_dir / "file_id.pkl"
        if not file_id_path.exists():
            raise DataNotFound
        with open(file_id_path, "rb") as f:
            return pickle.load(f)