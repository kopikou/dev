from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    postgres_name: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    echo: bool = False 

    secret_key: str = "valorant"
    secret_algorithm: str = "HS256"

    @property
    def db_url(self) -> str:
        # return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}".format(
        #     user=self.postgres_user,
        #     password=self.postgres_password,
        #     host=self.postgres_host,
        #     port=self.postgres_port,
        #     name=self.postgres_name,
        # )
        return "sqlite+aiosqlite:///./fastapi_db.sqlite3"


settings = Settings()
