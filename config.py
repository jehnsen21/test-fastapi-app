import os

class Settings:
    SECRET_kEY: str = os.getenv("SECRET_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()