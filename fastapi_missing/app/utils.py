import os
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from typing import Optional
import pandas as pd
from fastapi_missing.app.settings import settings
from fastapi_missing.app.exceptions import FilepathNotFoundException
from fastapi_missing.app.schemas import *

import base64
from io import BytesIO

class TempStorage:
    basedir = Path(settings.temp_dir)
    
    @classmethod
    def _ensure_temp_dir_exists(cls):
        """Создает временную директорию, если она не существует"""
        cls.basedir.mkdir(parents=True, exist_ok=True)
        os.chmod(cls.basedir, 0o755)

    @staticmethod
    def _generate_filename(filetype: ImageFormat = ImageFormat.PNG) -> str:
        """Генерирует уникальное имя файла"""
        timestamp = round(datetime.now().timestamp() * 100000)
        return f"{timestamp}.{filetype.value}"
    
    @staticmethod
    def _generate_data_filename(filetype: FileFormat = FileFormat.CSV) -> str:
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
            plt.rcParams['font.family'] = 'DejaVu Sans'
            
            if fig:
                fig.savefig(filepath, bbox_inches='tight', dpi=100)
            else:
                plt.savefig(filepath, bbox_inches='tight', dpi=100)
            return filename
        finally:
            if fig:
                plt.close(fig)
            plt.close('all') 

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
    
    @classmethod
    def return_dataframe(
        cls,
        df: pd.DataFrame,
        save_format: FileFormat = FileFormat.CSV,
    ) -> FileResponse:
        """Download DataFrame as CSV/Excel (работает только с FileFormat enum)"""
        cls._ensure_temp_dir_exists()
        filename = cls._generate_data_filename(save_format)
        filepath = cls.get_path(filename)
        
        if save_format == FileFormat.CSV:
            df.to_csv(filepath, index=False)
            media_type = "text/csv"
        elif save_format == FileFormat.EXCEL:
            df.to_excel(filepath, index=False)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type=media_type,
            background=BackgroundTask(cls.delete_file, filepath=str(filepath)),
        )
    
    @staticmethod
    def plot_to_base64() -> str:
        """Конвертирует текущий график matplotlib в base64 строку."""
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')