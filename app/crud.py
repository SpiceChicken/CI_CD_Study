# app/crud.py
from sqlalchemy.orm import Session
from app import models
import random
import string

# short_key 생성: 랜덤 문자열 생성
def generate_short_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# URL 삽입
def create_url(db: Session, target_url: str):
    short_key = generate_short_key()
    db_url = models.URL(target_url=target_url, short_key=short_key)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

# URL 찾기
def get_url(db: Session, short_key: str):
    return db.query(models.URL).filter(models.URL.short_key == short_key).first()

# URL 활성화 상태 변경
def deactivate_url(db: Session, short_key: str):
    db_url = db.query(models.URL).filter(models.URL.short_key == short_key).first()
    if db_url:
        db_url.is_active = 0
        db.commit()
        db.refresh(db_url)
    return db_url
