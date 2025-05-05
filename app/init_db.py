import sys
import os
from sqlalchemy.orm import Session

# 현재 경로 문제 해결
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine, get_db
from app.models import user as user_model
from app.core.security import hash_password

def init():
    user_model.Base.metadata.create_all(bind=engine)
    db: Session = next(get_db())

    # 기본 유저 존재 여부 확인
    existing_user = db.query(user_model.User).filter(user_model.User.email == "admin@example.com").first()
    if not existing_user:
        user = user_model.User(
            email="admin@example.com",
            hashed_password=hash_password("admin1234")
        )
        db.add(user)
        db.commit()
        print("✅ 기본 유저 생성 완료: admin@example.com / admin1234")
    else:
        print("ℹ️ 기본 유저가 이미 존재합니다.")

if __name__ == "__main__":
    init()
