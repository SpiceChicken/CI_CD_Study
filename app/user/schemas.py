# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User 모델 기반 스키마
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    # first_name: Optional[str] = None # 프로필 정보 추가 시 필요
    # last_name: Optional[str] = None  # 프로필 정보 추가 시 필요

class UserUpdate(BaseModel):
    # 프로필 정보 수정 시 사용
    # email: Optional[EmailStr] = None # 이메일 변경 가능 시
    # first_name: Optional[str] = None
    # last_name: Optional[str] = None
    # is_active: Optional[bool] = None # 관리자 권한으로 사용자 상태 변경 시 필요

    # 여기서는 일단 비밀번호 변경 기능만 고려하여 new_password를 추가할 수도 있지만,
    # 일반적으로 비밀번호 변경은 별도의 엔드포인트에서 현재 비밀번호 확인 후 진행합니다.
    pass # 현재는 프로필 수정 항목이 없으므로 빈 BaseModel로 둡니다.
    # 실제 구현 시 first_name, last_name 등을 추가

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool # 권한 관리 시 필요
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # SQLAlchemy 모델 객체를 Pydantic 모델로 변환 가능하게 함

# 인증 관련 스키마

# 리프레시 토큰 요청을 위한 스키마 (schemas.py에 추가하는 것을 권장합니다)
class RefreshTokenRequest(BaseModel):
    refresh_token: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None # 리프레시 토큰 사용 시 필요

class TokenData(BaseModel):
    sub: Optional[str] = None
    scopes: List[str] = [] # 권한 관리에 사용될 수 있습니다.

class UserLogin(UserBase):
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str # 이메일로 전송된 재설정 토큰
    new_password: str # 새 비밀번호

# 기타 스키마 (예: 성공/실패 메시지)
class Message(BaseModel):
    message: str

class PasswordResetByPowerUserRequest(BaseModel):
    """파워 유저가 다른 유저 비밀번호 초기화를 위한 요청 스키마"""
    target_user_email: EmailStr # 비밀번호를 초기화할 대상 사용자의 이메일

class ErrorResponse(BaseModel):
    detail: str