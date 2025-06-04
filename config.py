import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT", "https://localhost:8081")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY", "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "SampleDB")
    SECRET_kEY: str = os.getenv("SECRET_KEY", "cosmos_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
