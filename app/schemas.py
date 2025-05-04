# app/schemas.py
from pydantic import BaseModel

class URLCreate(BaseModel):
    target_url: str

    class Config:
        orm_mode = True

class URLResponse(BaseModel):
    id: int
    target_url: str
    short_key: str
    is_active: int  # URL 활성 상태

    class Config:
        orm_mode = True
