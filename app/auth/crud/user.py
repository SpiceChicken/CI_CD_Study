from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from app.security import verify_password, get_password_hash

# User CRUD 함수

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    return user if user and verify_password(password, user.hashed_password) else None

def get_user_by_email(db: Session, email: str):
    """이메일을 통해 사용자를 조회합니다."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """ID를 통해 사용자를 조회합니다."""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserCreate):
    """새로운 사용자를 생성합니다."""
    hashed_password = get_password_hash(user_in.password) # 실제 해싱 함수 사용
    db_user = User(
        hashed_password=hashed_password,
        **user_in.dict(exclude={'password'})
        # is_active, is_superuser 등은 모델에서 기본값 사용 또는 추가 가능
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_update: UserUpdate):
    """사용자 정보를 업데이트합니다."""
    # UserUpdate 스키마에 필드가 있다면 여기에서 업데이트 로직 구현
    # 예:
    # if user_update.first_name is not None:
    #     db_user.first_name = user_update.first_name
    # if user_update.last_name is not None:
    #     db_user.last_name = user_update.last_name
    # if user_update.is_active is not None:
    #     db_user.is_active = user_update.is_active

    # 비밀번호 변경은 별도 함수나 엔드포인트로 분리하는 것이 일반적입니다.
    # 예: change_password(db: Session, db_user: models.User, old_password: str, new_password: str)

    db.commit()
    db.refresh(db_user)
    return db_user