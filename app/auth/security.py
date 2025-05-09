import os
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Union

# OAuth2PasswordBearer는 클라이언트가 'Authorization: Bearer <token>' 형식으로 헤더를 전송하도록 합니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SECRET_KEY와 ALGORITHM을 설정에서 가져옵니다.
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# JWT 검증 함수
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # payload에서 'sub' (사용자 식별자 등)을 추출하여 사용할 수 있습니다.
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 인증이 필요한 API 엔드포인트에서 사용
def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)

# hash_password 함수 예시
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 비밀번호 검증 함수
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT 생성 함수
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    사용자 데이터를 받아 JWT 토큰을 생성하는 함수.
    :param data: JWT에 포함될 사용자 데이터 (예: 사용자 ID)
    :param expires_delta: 토큰의 만료 시간
    :return: 생성된 JWT 토큰
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})  # 만료 시간을 추가
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # 토큰 인코딩
    return encoded_jwt