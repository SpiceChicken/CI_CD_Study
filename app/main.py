# app/main.py
from fastapi import FastAPI
from app.routers import url
from app.database import engine, Base

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(url.router)
