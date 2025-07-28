import os
import pandas as pd

from datetime import datetime
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from fastapi_data.app.settings import settings
from fastapi_data.app.exceptions import FilepathNotFoundException
from fastapi_data.app.schemas import DataFormat, DataMediaType
from pathlib import Path


class TempStorage:
    basedir = Path(settings.temp_dir)
    @classmethod
    def ensure_temp_dir_exists(cls):
        """Создает временную директорию, если она не существует"""
        cls.basedir.mkdir(parents=True, exist_ok=True)
        os.chmod(cls.basedir, 0o755)

    @staticmethod
    def get_name(filetype: DataFormat = DataFormat.XLSX) -> str:
        return f"{round(datetime.now().timestamp() * 100000)}.{filetype.value}"

    @classmethod
    def get_path(cls, filename: str) -> str:
        return os.path.join(cls.basedir, filename)

    @classmethod
    def create_file(
        cls,
        df: pd.DataFrame,
        filetype: DataFormat = DataFormat.XLSX,
        index=False,
    ) -> str:
        cls.ensure_temp_dir_exists()
        filename = cls.get_name(filetype)
        filepath = cls.get_path(filename)

        if filetype == DataFormat.CSV:
            df.to_csv(filepath, encoding="utf-8", index=index)
        else:
            df.to_excel(filepath, index=index)
        return filename

    @classmethod
    def delete_file(cls, filepath: str):
        if not os.path.exists(filepath):
            raise FilepathNotFoundException
        os.remove(filepath)

    @classmethod
    def return_file(
        cls,
        df: pd.DataFrame,
        save_format: DataFormat = DataFormat.XLSX,
        index=False,
    ) -> FileResponse:
        cls.ensure_temp_dir_exists()
        filename = cls.create_file(df=df, filetype=save_format, index=index)
        filepath = cls.get_path(filename)
        media_type = getattr(DataMediaType, save_format.name).value

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=media_type,
            background=BackgroundTask(cls.delete_file, filepath=filepath),
        )
