# app/schemas.py: 요청/응답 데이터 모델(Pydantic 스키마) 정의 모듈
# - URLCreate: 단축 URL 생성 요청 스키마
# - URLResponse: 단축 URL 생성/조회 응답 스키마

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class URLCreate(BaseModel):
    """
    단축 URL 생성 요청 스키마
    - target_url: 단축하려는 원본 URL 문자열
    """
    target_url: str

    class Config:
        orm_mode = True  # ORM 모델(SQLAlchemy) 객체 직렬화 허용

class URLResponse(BaseModel):
    """
    단축 URL 생성/조회 응답 스키마
    - id: DB 내부 고유 식별자
    - target_url: 원본 URL
    - short_key: 생성된 단축 키
    - is_active: 활성 상태 (1=활성, 0=비활성)
    """
    id: int
    target_url: str
    short_key: str
    is_active: bool  # URL 활성 상태

    class Config:
        orm_mode = True  # ORM 모델을 JSON으로 자동 변환 허용

class URLStats(BaseModel):
    short_key: str
    target_url: str
    clicks: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]