# app/core/setting.py
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일을 읽어 환경 변수 설정

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "URL Shortener")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

settings = Settings()
