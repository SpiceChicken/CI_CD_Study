# app/api/shortener.py: URL 관련 API 엔드포인트 정의 모듈
# - POST /shorten: 단축 URL 생성
# - GET /{short_code}: 단축 URL 조회(리디렉션용 원본 URL 반환)
# - DELETE /{short_code}: 단축 URL 비활성화 처리
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from app.utils.url_valid import is_url_valid
from app.db.database import get_db

from app.shortener.crud import *
from app.shortener.models import URL
from app.shortener.schemas import *

from app.analytics.crud import log_click
from app.analytics.models import ClickLog

from app.utils.security import get_current_user
from app.user.models import User

router = APIRouter(
    prefix="/shortener/v1", # API 경로 접두사 설정
    tags=["shortener"]
)


# URL 단축 엔드포인트
@router.post("/shorten", response_model=URLResponse)
def shorten_url(url: URLCreate,db: Session = Depends(get_db)):
    """
    URL 단축 엔드포인트
    - 경로: POST /shorten
    - 요청 바디: URLCreate(target_url)
    - 동작: 원본 URL 저장 및 무작위 단축 키 생성
    - 반환: URLResponse(id, target_url, short_code, is_active)
    """

    # 입력된 URL이 유효한지 확인
    if not is_url_valid(url.target_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unreachable URL"
        )

    # URL이 유효하면 데이터베이스에 저장
    try:
        db_url = create_url(db, target_url=url.target_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create URL: {str(e)}"
        )
    
    return db_url

# 단축된 URL을 원본 URL로 리디렉션
@router.get("/{short_code}")
def redirect_to_target(short_code: str, request: Request ,db: Session = Depends(get_db)):
    """
    단축 URL 조회 엔드포인트
    - 경로: GET /{short_code}
    - 매개변수: short_code (path)
    - 동작: 단축 키로 URL 조회 후 활성 상태인 경우 원본 URL 반환
    - 에러: URL 미존재 또는 비활성 시 HTTP 404 예외
    """
    url = db.query(URL)\
            .filter(URL.short_code == short_code, URL.is_active)\
            .first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # 클릭 로그 기록
    log_click(
        db=db,
        code=short_code,
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # 클릭 수 증가
    url.clicks += 1
    db.commit()
    return RedirectResponse(url.target_url)

# URL 비활성화 엔드포인트
@router.delete("/{short_code}")
def deactivate_url(short_code: str, db: Session = Depends(get_db)):
    """
    URL 비활성화 엔드포인트
    - 경로: DELETE /{short_code}
    - 매개변수: short_code (path)
    - 동작: URL의 is_active를 0으로 변경
    - 반환: 성공 메시지 JSON
    - 에러: 키 미존재 시 HTTP 404 예외 발생
    """
    db_url = deactivate_url_from_db(db=db, short_code=short_code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"message": "URL successfully deactivated"}

# URL 클릭 정보 조회
@router.get("/urls/{short_code}")
def get_click_info(short_code: str, db: Session = Depends(get_db)):
    """
    단축 URL 클릭 정보 조회
    - 경로: GET /urls/{short_code}
    - 매개변수: short_code (path)
    - 반환: target_url, clicks, is_active
    """
    url = db.query(URL).filter(URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return {
        "target_url": url.target_url,
        "clicks": url.clicks,
        "is_active": url.is_active
    }

# URL 통계 조회 (클릭 수 등)
@router.get("/stats/{short_code}", response_model=URLStats)
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    """
    단축 URL 통계 조회
    - 경로: GET /stats/{short_code}
    - 반환: target_url, clicks, is_active
    """
    db_url = get_url_stats_from_db(db=db, short_code=short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    return db_url