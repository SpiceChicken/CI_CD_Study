# app/schemas/token.py

from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None  # 리프레시 토큰 사용 시 필요

class TokenData(BaseModel):
    sub: Optional[str] = None
    scopes: List[str] = []

class RefreshTokenRequest(BaseModel):
    refresh_token: str
