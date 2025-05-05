# app/crud.py: 데이터베이스 CRUD 로직 모듈
# - URL 단축 키 생성, URL 생성/조회/비활성화 함수 정의

import random
import string
from sqlalchemy.orm import Session
from app import models

def generate_short_key(length: int = 6) -> str:
    """
    지정된 길이의 무작위 단축 키를 생성합니다.
    - length: 생성할 키의 길이 (기본값 6)
    - 반환: 영문 대소문자와 숫자로 구성된 문자열
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_url(db: Session, target_url: str) -> models.URL:
    """
    새 URL 레코드를 생성하고 단축 키를 자동으로 할당합니다.
    - db: SQLAlchemy 세션
    - target_url: 단축할 원본 URL 문자열
    동작:
      1. generate_short_key로 단축 키 생성
      2. models.URL 객체 생성 및 세션에 추가
      3. 커밋(commit) 및 새로고침(refresh)하여 DB 저장된 객체 반환
    - 반환: 생성된 URL 모델 객체
    """
    short_key = generate_short_key()
    db_url = models.URL(target_url=target_url, short_key=short_key)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def get_url(db: Session, short_key: str) -> models.URL:
    """
    주어진 단축 키로 URL 레코드를 조회합니다.
    - db: SQLAlchemy 세션
    - short_key: 조회할 단축 키 문자열
    - 반환: URL 모델 객체 또는 None
    """
    return db.query(models.URL).filter(models.URL.short_key == short_key).first()

def deactivate_url(db: Session, short_key: str) -> models.URL:
    """
    주어진 단축 키의 URL 레코드를 비활성화 처리합니다.
    - db: SQLAlchemy 세션
    - short_key: 비활성화할 단축 키 문자열
    동작:
      1. 해당 키로 URL 레코드 조회
      2. is_active를 0(비활성)으로 변경
      3. 커밋 및 새로고침 후 업데이트된 객체 반환
    - 반환: 업데이트된 URL 모델 객체 또는 None
    """
    db_url = db.query(models.URL).filter(models.URL.short_key == short_key).first()
    if db_url:
        db_url.is_active = 0
        db.commit()
        db.refresh(db_url)
    return db_url
