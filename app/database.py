# app/database.py: 데이터베이스 연결 및 ORM 설정 모듈
# - 환경 변수 또는 기본값을 사용해 데이터베이스 URL 설정
# - SQLAlchemy 엔진(engine) 생성 및 세션팩토리(SessionLocal) 설정
# - ORM 모델(Base) 정의 준비
# - FastAPI 의존성(get_db)으로 DB 세션 제공

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 환경 변수에서 DATABASE_URL을 읽어옵니다. 없으면 기본값(postgresql://postgres:postgres@db:5432/url_db)을 사용
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/url_db")

# SQLAlchemy 엔진 생성: DB 연결을 관리하는 주요 객체
engine = create_engine(DATABASE_URL)

# 세션팩토리 설정: DB 트랜잭션 단위로 세션(SessionLocal)을 생성하는 공장 함수
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스: ORM 모델 클래스들이 상속받아 테이블 메타데이터를 축적
Base = declarative_base()

def get_db():
    """
    FastAPI 의존성 함수
    - 요청이 들어올 때마다 새로운 DB 세션을 생성
    - 요청 처리 후 세션을 안전하게 종료(반납)함
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
