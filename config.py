from decouple import config
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    COSMOS_ENDPOINT: str = config("COSMOS_ENDPOINT")
    COSMOS_KEY: str = config("COSMOS_KEY")
    DATABASE_NAME: str = config("DATABASE_NAME")
    SECRET_kEY: str = config("SECRET_KEY", "cosmos_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
