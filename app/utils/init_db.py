import sys
import os
from sqlalchemy.orm import Session

# 현재 경로 문제 해결
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, get_db
from app.user import models as user_model
from app.shortener import models as shortener_model
from app.utils.security import get_password_hash
from app.shortener.crud import generate_short_code

DEFAULT_EMAIL = os.getenv("DEFAULT_USER_EMAIL")
DEFAULT_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD")

def init():
    user_model.Base.metadata.create_all(bind=engine)
    shortener_model.Base.metadata.create_all(bind=engine)

    db: Session = next(get_db())

    # 기본 유저 생성
    user = db.query(user_model.User).filter_by(email=DEFAULT_EMAIL).first()
    if not user:
        user = user_model.User(
            email=DEFAULT_EMAIL,
            hashed_password=get_password_hash(DEFAULT_PASSWORD),
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
                short_code=generate_short_code(db=db),
            )
            db.add(new_url)

    db.commit()
    print("✅ DB 초기화 완료")

if __name__ == "__main__":
    init()
