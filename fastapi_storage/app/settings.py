from pydantic_settings import BaseSettings

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    postgres_name: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    echo: bool = False

    storage_dir: str = str(BASE_DIR / "media" / "fdb_integration" / "storage")

    auth_host: str = "127.0.0.1"
    auth_port: str = "8000"

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

    @property
    def auth_url(self) -> str:
        return "http://{host}:{port}".format(
            host=self.auth_host,
            port=self.auth_port,
        )


settings = Settings()
