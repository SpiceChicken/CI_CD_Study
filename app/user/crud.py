from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta # 토큰 만료 시간 설정에 사용
from app.utils.security import get_password_hash, verify_password # 실제 비밀번호 해싱/검증 함수 (별도 구현 필요)

# User CRUD 함수

def get_user_by_email(db: Session, email: str):
    """이메일을 통해 사용자를 조회합니다."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """ID를 통해 사용자를 조회합니다."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    """새로운 사용자를 생성합니다."""
    hashed_password = get_password_hash(user.password) # 실제 해싱 함수 사용
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        # is_active, is_superuser 등은 모델에서 기본값 사용 또는 추가 가능
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, user_update: schemas.UserUpdate):
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

# Token CRUD 함수

def create_token(db: Session, token: str, token_type: str, user_id: int, expires_delta: timedelta = None):
    """새로운 토큰 정보를 저장합니다."""
    expires_at = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15)) # 기본 만료 시간
    db_token = models.Token(
        token=token,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_token_by_value(db: Session, token: str, token_type: str):
    """토큰 값과 타입으로 토큰 정보를 조회합니다."""
    return db.query(models.Token).filter(
        models.Token.token == token,
        models.Token.token_type == token_type
    ).first()

def get_valid_password_reset_token(db: Session, token: str):
    """유효한 비밀번호 재설정 토큰을 조회합니다."""
    # 현재 시간 기준으로 만료되지 않은 토큰만 조회
    return db.query(models.Token).filter(
        models.Token.token == token,
        models.Token.token_type == 'reset',
        models.Token.expires_at > datetime.utcnow()
    ).first()


def delete_token(db: Session, db_token: models.Token):
    """토큰 정보를 삭제합니다."""
    db.delete(db_token)
    db.commit()
