from sqlalchemy.orm import Session
from ..models.token import Token

from datetime import datetime, timedelta

# Token CRUD 함수
def create_token(db: Session, token: str, token_type: str, user_id: int, expires_delta: timedelta = None):
    """새로운 토큰 정보를 저장합니다."""
    expires_at = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15)) # 기본 만료 시간
    db_token = Token(
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
    return db.query(Token).filter(
        Token.token == token,
        Token.token_type == token_type
    ).first()

def get_valid_password_reset_token(db: Session, token: str):
    """유효한 비밀번호 재설정 토큰을 조회합니다."""
    # 현재 시간 기준으로 만료되지 않은 토큰만 조회
    return db.query(Token).filter(
        Token.token == token,
        Token.token_type == 'reset',
        Token.expires_at > datetime.utcnow()
    ).first()


def delete_token(db: Session, db_token: Token):
    """토큰 정보를 삭제합니다."""
    db.delete(db_token)
    db.commit()