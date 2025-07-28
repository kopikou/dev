import pandas as pd
from fastapi_missing.app.exceptions import DataNotFound

class ValidateData:
    @staticmethod
    def check_dataframe(df: pd.DataFrame) -> None:
        if df.empty:
            raise DataNotFound("Загруженный DataFrame пуст")
        
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Данные должны быть в формате pandas DataFrame")