import pandas as pd
import pickle

from pathlib import Path
from fastapi_visualization.app.settings import settings
from fastapi_visualization.app.exceptions import DataNotFound

class LocalStorage:
    @staticmethod
    def _get_user_dir(user_id: str) -> Path:
        """Создает папку для хранения данных пользователя"""
        user_dir = Path(settings.storage_dir) / "user_data" / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    @classmethod
    async def set_dataframe(cls, user_id: str, df: pd.DataFrame, file_id: int | None = None):
        user_dir = cls._get_user_dir(user_id)
        df.to_pickle(user_dir / "data.pkl")
        if file_id is not None:
            with open(user_dir / "file_id.pkl", "wb") as f:
                pickle.dump(file_id, f)

    @classmethod
    async def set_file_id(cls, user_id: str, file_id: int):
        user_dir = cls._get_user_dir(user_id)
        with open(user_dir / "file_id.pkl", "wb") as f:
            pickle.dump(file_id, f)

    @classmethod
    async def get_dataframe(cls, user_id: str) -> pd.DataFrame:
        user_dir = cls._get_user_dir(user_id)
        data_path = user_dir / "data.pkl"
        if not data_path.exists():
            raise DataNotFound
        return pd.read_pickle(data_path)

    @classmethod
    async def get_file_id(cls, user_id: str) -> int:
        user_dir = cls._get_user_dir(user_id)
        file_id_path = user_dir / "file_id.pkl"
        if not file_id_path.exists():
            raise DataNotFound
        with open(file_id_path, "rb") as f:
            return pickle.load(f)