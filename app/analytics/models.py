from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.db.database import Base

class ClickLog(Base):
    __tablename__ = "click_logs"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, ForeignKey("urls.short_code"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    client_ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)