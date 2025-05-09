from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.database import get_db

from app.analytics.crud import *
from app.analytics.models import *
from app.analytics.schemas import *

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/{code}", response_model=AnalyticsResponse)
def read_analytics(code: str, db: Session = Depends(get_db)):
    """단축코드의 전체 클릭 수와 로그 목록을 반환"""
    logs = get_clicks(db, code)
    return AnalyticsResponse(
        total_clicks=len(logs),
        logs=logs,
    )

# Shortener redirect 로직에 로깅 추가 예시:
# from fastapi.responses import RedirectResponse
# @router.get("/redirect/{code}")
# def redirect_and_log(code: str, request: Request, db: Session = Depends(get_db)):
#     log = crud.log_click(db, code, request.client.host, request.headers.get('user-agent'))
#     return RedirectResponse(existing_url)