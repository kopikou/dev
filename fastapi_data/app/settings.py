from pydantic_settings import BaseSettings

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    auth_host: str = "127.0.0.1"
    auth_port: str = "8000"

    storage_host: str = "127.0.0.1"
    storage_port: str = "8001"

    storage_dir: str = str(BASE_DIR / "media" / "fdb_integration" / "storage")
    temp_dir: str = str(BASE_DIR / "media" / "fdb_integration" / "temp")

    def get_url(self, host: str, port: str):
        return "http://{host}:{port}".format(
            host=host,
            port=port,
        )

    @property
    def auth_url(self) -> str:
        return self.get_url(self.auth_host, self.auth_port)

    @property
    def storage_url(self) -> str:
        return self.get_url(self.storage_host, self.storage_port)


settings = Settings()
