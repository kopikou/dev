import httpx
import pandas as pd

from io import BytesIO

from fastapi_data.app.settings import settings
from fastapi_data.app.exceptions import MirrorHTTPException, ServerException
from fastapi_data.app.schemas import DataFormat, DataMediaType
from fastapi_data.app.utils import TempStorage
from fastapi_data.app.data.exceptions import LoadCSVException, CSVSepException
import logging
from fastapi import HTTPException

# Get a logger instance for your module
logger = logging.getLogger(__name__)

class StorageServiceRequests:
    @staticmethod
    async def get_user_file(
        user_token: str, file_id: int, sep: str | None = None
    ) -> pd.DataFrame:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Requesting file {file_id} from storage service")
                response = await client.get(
                    f"{settings.storage_url}/storage/download/{file_id}",
                    headers={"Authorization": f"Bearer {user_token}"},
                )
                
                logger.info(f"Response status: {response.status_code}")
                
                # Обработка ошибок
                if response.status_code != 200:
                    error_detail = response.text if response.text else "No error details"
                    logger.error(f"Storage service error: {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Storage service error: {error_detail}"
                    )

                # Проверка содержимого
                if not response.content:
                    logger.error("Received empty file content")
                    raise HTTPException(status_code=404, detail="File is empty")

                file_obj = BytesIO(response.content)
                
                # Определение типа файла
                try:
                    if response.content.startswith(b"PK\x03\x04") or response.content.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
                        logger.info("Loading Excel file")
                        df = pd.read_excel(file_obj)
                    else:
                        logger.info("Loading CSV file")
                        sep = sep if sep else ","
                        df = pd.read_csv(file_obj, sep=sep)
                except Exception as e:
                    logger.error(f"File parsing error: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Invalid file format: {str(e)}")

                # Нормализация столбцов
                df = df.rename(columns={col: col.strip() for col in df.columns})
                return df

        except httpx.RequestError as e:
            logger.error(f"Request to storage service failed: {str(e)}")
            raise HTTPException(status_code=503, detail="Storage service unavailable")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def sent_file(
        user_token: str, file_id: int, file_obj: BytesIO, filetype: DataFormat
    ) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                media_type = getattr(DataMediaType, filetype.name).value
                filename = TempStorage.get_name(filetype=filetype)

                response = await client.post(
                    f"{settings.storage_url}/storage/add/version",
                    headers={"Authorization": f"Bearer {user_token}"},
                    params={"based_file_id": file_id},
                    files={
                        "upload_file_obj": (
                            filename,
                            file_obj,
                            media_type,
                        )
                    },
                )
        except Exception:
            raise ServerException

        if response.status_code != 201:
            raise MirrorHTTPException(response)

        return response.json()
