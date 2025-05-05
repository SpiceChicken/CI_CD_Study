# app/main.py: FastAPI 서버 진입점 및 라우터 설정 모듈
#
# 이 파일은 FastAPI 애플리케이션을 초기화하고,
# 데이터베이스 테이블을 생성(Base.metadata.create_all)하며,
# URL 단축 기능을 제공하는 라우터를 등록합니다.

from fastapi import FastAPI
from app.routers import url
from app.database import engine, Base

# 데이터베이스 테이블 생성: 정의된 ORM 모델을 기반으로 실제 테이블을 생성하거나 반영합니다.
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스 생성: 엔드포인트 등록 및 요청/응답 처리 준비
app = FastAPI()

# URL 관련 라우터 등록: 단축, 리디렉션, 비활성화 엔드포인트 활성화
app.include_router(url.router)