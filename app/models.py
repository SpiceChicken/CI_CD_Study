# app/models.py
from sqlalchemy import Column, Integer, String
from app.database import Base  # SQLAlchemy Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    short_key = Column(String, unique=True, index=True)  # 단축된 키
    is_active = Column(Integer, default=1)  # URL 활성 상태 (1: 활성, 0: 비활성)