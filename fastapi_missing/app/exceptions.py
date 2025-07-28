from fastapi import status
from fastapi.exceptions import HTTPException

DataNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Для начала необходимо загрузить данные!",
)

class MissingDataThresholdException(HTTPException):
    def __init__(self, threshold: float):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Порог восстановления ({threshold*100}%) слишком высок. Рекомендуется значение до 30%",
        )

class InvalidImputationMethodException(HTTPException):
    def __init__(self, method: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый метод импутации: {method}",
        )

class MirrorHTTPException(HTTPException):
    def __init__(self, response):
        try:
            text = json.loads(response.text).get("detail")
        except:
            text = response.text
        super().__init__(
            status_code=response.status_code,
            detail=text
        )

class FilepathNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл по указанному пути не найден!"
        )