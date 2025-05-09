from sqlalchemy.orm import Session
from app.analytics.models import ClickLog

def log_click(db: Session, code: str, client_ip: str | None, user_agent: str | None):
    db_obj = ClickLog(
        short_code=code,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_clicks(db: Session, code: str):
    logs = db.query(ClickLog).filter(ClickLog.short_code == code).all()
    return logs