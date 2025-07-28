import httpx
import pandas as pd

from io import BytesIO

from fastapi_data.app.settings import settings
from fastapi_data.app.exceptions import MirrorHTTPException, ServerException
from fastapi_data.app.schemas import DataFormat, DataMediaType
from fastapi_data.app.utils import TempStorage
from fastapi_data.app.data.exceptions import LoadCSVException, CSVSepException
import logging

# Get a logger instance for your module
logger = logging.getLogger(__name__)

class StorageServiceRequests:
    @staticmethod
    async def get_user_file(
        user_token: str, file_id: int, sep: str | None = None
    ) -> pd.DataFrame:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.storage_url}/storage/download/{file_id}",
                headers={"Authorization": f"Bearer {user_token}"},
            )
        logger.info(f"File {file_id} received, size: {len(response.content)} bytes")
        if response.status_code != 200:
            raise MirrorHTTPException(response)

        response_content = response.content
        file_obj = BytesIO(response_content)
        if response_content.startswith(b"PK\x03\x04") or response_content.startswith(
            b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
        ):
            df = pd.read_excel(file_obj)
        else:
            if sep is None:
                raise CSVSepException
            try:
                df = pd.read_csv(file_obj, sep=sep)
            except Exception:
                raise LoadCSVException

        return df

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
