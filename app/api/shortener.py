# app/api/shortener.py: URL 관련 API 엔드포인트 정의 모듈
# - POST /shorten: 단축 URL 생성
# - GET /{short_key}: 단축 URL 조회(리디렉션용 원본 URL 반환)
# - DELETE /{short_key}: 단축 URL 비활성화 처리
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from app.utils import url_valid
from app.crud import shortener as crud_shortener
from app.db import session
from app.models import shortener as model_shortener
from app.schemas import shortener as schema_shortener
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

# URL 단축 엔드포인트
@router.post("/shorten", response_model=schema_shortener.URLResponse)
def shorten_url(url: schema_shortener.URLCreate,db: Session = Depends(session.get_db)):
    """
    URL 단축 엔드포인트
    - 경로: POST /shorten
    - 요청 바디: URLCreate(target_url)
    - 동작: 원본 URL 저장 및 무작위 단축 키 생성
    - 반환: URLResponse(id, target_url, short_key, is_active)
    """

    # 입력된 URL이 유효한지 확인
    if not url_valid.is_url_valid(url.target_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unreachable URL"
        )

    # URL이 유효하면 데이터베이스에 저장
    try:
        db_url = crud_shortener.create_url(db, target_url=url.target_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create URL: {str(e)}"
        )
    
    return db_url

# 단축된 URL을 원본 URL로 리디렉션
@router.get("/{short_key}")
def redirect_to_target(short_key: str, db: Session = Depends(session.get_db)):
    """
    단축 URL 조회 엔드포인트
    - 경로: GET /{short_key}
    - 매개변수: short_key (path)
    - 동작: 단축 키로 URL 조회 후 활성 상태인 경우 원본 URL 반환
    - 에러: URL 미존재 또는 비활성 시 HTTP 404 예외
    """
    url = db.query(model_shortener.URL)\
            .filter(model_shortener.URL.short_key == short_key, model_shortener.URL.is_active)\
            .first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    # 클릭 수 증가
    url.clicks += 1
    db.commit()
    return RedirectResponse(url.target_url)

# URL 비활성화 엔드포인트
@router.delete("/{short_key}")
def deactivate_url(short_key: str, db: Session = Depends(session.get_db)):
    """
    URL 비활성화 엔드포인트
    - 경로: DELETE /{short_key}
    - 매개변수: short_key (path)
    - 동작: URL의 is_active를 0으로 변경
    - 반환: 성공 메시지 JSON
    - 에러: 키 미존재 시 HTTP 404 예외 발생
    """
    db_url = crud_shortener.deactivate_url(db, short_key=short_key)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"message": "URL successfully deactivated"}

# URL 클릭 정보 조회
@router.get("/urls/{short_key}")
def get_click_info(short_key: str, db: Session = Depends(session.get_db)):
    """
    단축 URL 클릭 정보 조회
    - 경로: GET /urls/{short_key}
    - 매개변수: short_key (path)
    - 반환: target_url, clicks, is_active
    """
    url = db.query(model_shortener.URL).filter(model_shortener.URL.short_key == short_key).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return {
        "target_url": url.target_url,
        "clicks": url.clicks,
        "is_active": url.is_active
    }

# URL 통계 조회 (클릭 수 등)
@router.get("/stats/{short_key}", response_model=schema_shortener.URLStats)
def get_url_stats(short_key: str, db: Session = Depends(session.get_db)):
    """
    단축 URL 통계 조회
    - 경로: GET /stats/{short_key}
    - 반환: target_url, clicks, is_active
    """
    db_url = crud_shortener.get_url_stats(db, short_key=short_key)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    return db_url
