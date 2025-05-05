# app/routers/url.py: URL 관련 API 엔드포인트 정의 모듈
# - POST /shorten: 단축 URL 생성
# - GET /{short_key}: 단축 URL 조회(리디렉션용 원본 URL 반환)
# - DELETE /{short_key}: 단축 URL 비활성화 처리
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from app import crud, schemas, database, models, utils

router = APIRouter()
# APIRouter 인스턴스: URL 관련 엔드포인트 그룹 관리

# URL 단축 엔드포인트
@router.post("/shorten", response_model=schemas.URLResponse)
def shorten_url(url: schemas.URLCreate, db: Session = Depends(database.get_db)):
    """
    URL 단축 엔드포인트
    - 경로: POST /shorten
    - 요청 바디: URLCreate(target_url)
    - 동작: 원본 URL 저장 및 무작위 단축 키 생성
    - 반환: URLResponse(id, target_url, short_key, is_active)
    """
    # 입력된 URL이 유효한지 확인
    if not utils.is_url_valid(url.target_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unreachable URL"
        )

    # URL이 유효하면 데이터베이스에 저장
    try:
        db_url = crud.create_url(db, target_url=url.target_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create URL: {str(e)}"
        )
    
    return db_url

# 단축된 URL을 원본 URL로 리디렉션
@router.get("/{short_key}")
def redirect_to_target(short_key: str, db: Session = Depends(database.get_db)):
    """
    단축 URL 조회 엔드포인트
    - 경로: GET /{short_key}
    - 매개변수: short_key (path)
    - 동작: 단축 키로 URL 조회 후 활성 상태인 경우 원본 URL 반환
    - 에러: URL 미존재 또는 비활성 시 HTTP 404 예외
    """
    url = db.query(models.URL)\
            .filter(models.URL.short_key == short_key, models.URL.is_active)\
            .first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    url.clicks += 1
    db.commit()
    return RedirectResponse(url.target_url)

# URL 비활성화 엔드포인트
@router.delete("/{short_key}")
def deactivate_url(short_key: str, db: Session = Depends(database.get_db)):
    """
    URL 비활성화 엔드포인트
    - 경로: DELETE /{short_key}
    - 매개변수: short_key (path)
    - 동작: URL의 is_active를 0으로 변경
    - 반환: 성공 메시지 JSON
    - 에러: 키 미존재 시 HTTP 404 예외 발생
    """
    db_url = crud.deactivate_url(db, short_key=short_key)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"message": "URL successfully deactivated"}

@router.get("/urls/{short_key}")
def get_click_info(short_key: str, db: Session = Depends(database.get_db)):
    url = db.query(models.URL).filter(models.URL.short_key == short_key).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return {
        "target_url": url.target_url,
        "clicks": url.clicks,
        "is_active": url.is_active
    }

@router.get("/stats/{short_key}", response_model=schemas.URLStats)
def get_url_stats(short_key: str, db: Session = Depends(database.get_db)):
    db_url = crud.get_url_stats(db, short_key=short_key)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    return db_url