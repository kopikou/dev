import os
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from typing import Optional

from fastapi_visualization.app.settings import settings
from fastapi_visualization.app.exceptions import FilepathNotFoundException
from fastapi_visualization.app.schemas import ImageFormat, ImageMediaType


class TempStorage:
    basedir = Path(settings.temp_dir)
    
    @classmethod
    def _ensure_temp_dir_exists(cls):
        """Создает временную директорию, если она не существует"""
        cls.basedir.mkdir(parents=True, exist_ok=True)
        # Устанавливаем безопасные права доступа
        os.chmod(cls.basedir, 0o755)

    @staticmethod
    def _generate_filename(filetype: ImageFormat = ImageFormat.PNG) -> str:
        """Генерирует уникальное имя файла"""
        timestamp = round(datetime.now().timestamp() * 100000)
        return f"{timestamp}.{filetype.value}"

    @classmethod
    def get_path(cls, filename: str) -> Path:
        """Возвращает полный путь к файлу"""
        return cls.basedir / filename

    @classmethod
    def create_file(
        cls,
        filetype: ImageFormat = ImageFormat.PNG,
        fig: Optional[plt.Figure] = None
    ) -> str:
        """Создает временный файл изображения"""
        cls._ensure_temp_dir_exists()
        filename = cls._generate_filename(filetype)
        filepath = cls.get_path(filename)
        
        try:
            # Сохраняем текущую фигуру или переданную явно
            (fig or plt).savefig(filepath, bbox_inches='tight', dpi=100)
            return filename
        finally:
            if fig:
                plt.close(fig)
            else:
                plt.close()

    @classmethod
    def delete_file(cls, filepath: str):
        """Удаляет временный файл"""
        path = Path(filepath)
        if not path.exists():
            raise FilepathNotFoundException(f"File not found: {filepath}")
        
        try:
            path.unlink()
        except Exception as e:
            raise FilepathNotFoundException(f"Failed to delete file: {str(e)}")

    @classmethod
    def return_file(
        cls,
        save_format: ImageFormat = ImageFormat.PNG,
        fig: Optional[plt.Figure] = None
    ) -> FileResponse:
        """Возвращает FileResponse с временным файлом изображения"""
        filename = cls.create_file(filetype=save_format, fig=fig)
        filepath = cls.get_path(filename)
        media_type = getattr(ImageMediaType, save_format.name).value

        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type=media_type,
            background=BackgroundTask(cls.delete_file, filepath=str(filepath)),
        )