import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.auth.models.token import Token
from app.auth.models.user import User
from app.db.database import get_db
from app.auth import crud

ALGORITHM = os.getenv("ALGORITHM","HS256")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/v1/login/oauth2/")

def verify_password(plain_password, hashed_password):
    """
    사용자가 입력한 비밀번호와 DB에 저장된 해시된 비밀번호를 비교합니다.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    사용자가 입력한 비밀번호를 해시화 합니다.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    JMT 토큰을 생성 합니다.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    """
    JWT 리프레시 토큰을 생성합니다.
    """
    encoded_jwt = create_access_token(data=data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    현재 User를 확인합니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = Token(email=email)
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# 관리자 권한 확인 의존성 (기존 코드)
def get_current_active_superuser(current_user: User = Depends(get_current_user)):
    """
    SuperUser 권한을 확인합니다.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return current_user
