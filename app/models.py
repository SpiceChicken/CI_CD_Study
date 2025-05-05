# app/models.py: SQLAlchemy ORM 모델 정의 모듈
# - URL: urls 테이블 매핑 모델 (원본 URL, 단축 키, 활성 상태 관리)
from sqlalchemy import Column, Integer, String
from app.database import Base  # SQLAlchemy Base

class URL(Base):
    """
    URLs 테이블 ORM 모델 클래스
    - id: 고유 식별자 (Primary Key)
    - target_url: 저장할 원본 URL
    - short_key: 생성된 단축 키 (Unique)
    - is_active: 활성 상태 표시 (1=활성, 0=비활성)
    """
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    short_key = Column(String, unique=True, index=True)  # 단축된 키
    is_active = Column(Integer, default=1)  # URL 활성 상태 (1: 활성, 0: 비활성)