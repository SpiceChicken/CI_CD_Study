# app/crud.py: 데이터베이스 CRUD 로직 모듈
# - URL 단축 키 생성, URL 생성/조회/비활성화 함수 정의

import random
import string
import secrets
from sqlalchemy.orm import Session
from app.shortener.models import URL

def generate_short_key(db: Session, length: int = 6) -> str:
    """
    지정된 길이의 무작위 단축 키를 생성합니다.
    - length: 생성할 키의 길이 (기본값 6)
    - 반환: 영문 대소문자와 숫자로 구성된 문자열
    """
    while True:
        key = secrets.token_urlsafe(length)[:length]
        exists = db.query(URL).filter_by(short_key=key).first()
        if not exists:
            return key

def get_url_by_target_url(db: Session, target_url: str) -> URL:
    """
    주어진 원본 URL로 URL 레코드를 조회합니다.
    - db: SQLAlchemy 세션
    - target_url: 조회할 원본 URL 문자열
    - 반환: URL 모델 객체 또는 None
    """
    return db.query(URL).filter(URL.target_url == target_url).first()

def create_url(db: Session, target_url: str) -> URL:
    """
    새 URL 레코드를 생성하고 단축 키를 자동으로 할당합니다.
    - db: SQLAlchemy 세션
    - target_url: 단축할 원본 URL 문자열
    동작:
      1. 이미 존재하는 URL인지 확인
      2. 존재하면 해당 URL 반환
      3. 존재하지 않으면 새로 생성
    - 반환: 생성된 URL 모델 객체 또는 기존 URL 모델 객체
    """
    # 이미 존재하는 URL인지 확인
    existing_url = get_url_by_target_url(db, target_url=target_url)
    if existing_url:
        return existing_url
        
    short_key = generate_short_key(db=db)
    db_url = URL(target_url=target_url, short_key=short_key)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def get_url(db: Session, short_key: str) -> URL:
    """
    주어진 단축 키로 URL 레코드를 조회합니다.
    - db: SQLAlchemy 세션
    - short_key: 조회할 단축 키 문자열
    - 반환: URL 모델 객체 또는 None
    """
    return db.query(URL).filter(URL.short_key == short_key).first()

def deactivate_url(db: Session, short_key: str) -> URL:
    """
    주어진 단축 키의 URL 레코드를 비활성화 처리합니다.
    - db: SQLAlchemy 세션
    - short_key: 비활성화할 단축 키 문자열
    동작:
      1. 해당 키로 URL 레코드 조회
      2. is_active를 False(비활성)으로 변경
      3. 커밋 및 새로고침 후 업데이트된 객체 반환
    - 반환: 업데이트된 URL 모델 객체 또는 None
    """
    db_url = db.query(URL).filter(URL.short_key == short_key).first()
    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
    return db_url

def get_url_stats(db: Session, short_key: str):
    return db.query(URL).filter(URL.short_key == short_key).first()
