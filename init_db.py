import sys
import os
from sqlalchemy.orm import Session

# 현재 경로 문제 해결
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine, get_db
from app.models import user as user_model
from app.models import shortener as shortener_model
from app.core.security import hash_password
from app.crud.shortener import generate_short_key

DEFAULT_EMAIL = os.getenv("DEFAULT_USER_EMAIL", "admin@example.com")
DEFAULT_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD", "admin123")

def init():
    user_model.Base.metadata.create_all(bind=engine)
    shortener_model.Base.metadata.create_all(bind=engine)

    db: Session = next(get_db())

    # 기본 유저 생성
    user = db.query(user_model.User).filter_by(email=DEFAULT_EMAIL).first()
    if not user:
        user = user_model.User(
            email=DEFAULT_EMAIL,
            hashed_password=hash_password(DEFAULT_PASSWORD),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 더미 URL 생성
    dummy_urls = [
        "https://fastapi.tiangolo.com",
        "https://www.python.org",
        "https://www.postgresql.org",
    ]

    for original_url in dummy_urls:
        exists = db.query(shortener_model.URL).filter_by(target_url=original_url).first()
        if not exists:
            new_url = shortener_model.URL(
                target_url=original_url,
                short_key=generate_short_key(db=db),
            )
            db.add(new_url)

    db.commit()
    print("✅ DB 초기화 완료")

if __name__ == "__main__":
    init()
