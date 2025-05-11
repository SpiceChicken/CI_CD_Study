from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

from app.analytics.crud import *
from app.analytics.models import *
from app.analytics.schemas import *

router = APIRouter(
    prefix="/analytics/v1", # API 경로 접두사 설정
    tags=["analytics"])

@router.get("/{code}", response_model=AnalyticsResponse)
def read_analytics(code: str, db: Session = Depends(get_db)):
    """단축코드의 전체 클릭 수와 로그 목록을 반환"""
    click_logs = get_clicks(db, code)
    click_logs_infos: list[ClickLogInfo] = []
    for log_entry in click_logs:
        click_log_info_entry = ClickLogInfo(           
            timestamp=log_entry.timestamp,
            client_ip=log_entry.client_ip,
            user_agent=log_entry.user_agent
        )
        click_logs_infos.append(click_log_info_entry)
    
    return AnalyticsResponse(
        total_clicks=len(click_logs),
        logs=click_logs_infos,
    )