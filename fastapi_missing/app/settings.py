from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    auth_host: str = "auth_service"
    auth_port: str = "8000"
    redis_host: str = "redis"
    redis_port: str = "6379"
    temp_dir: str = "temp"

    @property
    def auth_url(self) -> str:
        return f"http://{self.auth_host}:{self.auth_port}"

settings = Settings()