# app/main.py: FastAPI 서버 진입점 및 라우터 설정 모듈
#
# 이 파일은 FastAPI 애플리케이션을 초기화하고,
# 데이터베이스 테이블을 생성(Base.metadata.create_all)하며,
# URL 단축 기능을 제공하는 라우터를 등록합니다.

from fastapi import FastAPI
from app.api import shortener, auth
from app.db.session import Base, engine

app = FastAPI(title="URL Shortener with Auth")

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(shortener.router, prefix="/api/shortener", tags=["shortener"])

# 자동 테이블 생성 (개발용)
Base.metadata.create_all(bind=engine)