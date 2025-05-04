# app/routers/url.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, database

router = APIRouter()

# URL 단축 엔드포인트
@router.post("/shorten", response_model=schemas.URLResponse)
def shorten_url(url: schemas.URLCreate, db: Session = Depends(database.get_db)):
    db_url = crud.create_url(db, target_url=url.target_url)
    return db_url

# 단축된 URL을 원본 URL로 리디렉션
@router.get("/{short_key}")
def redirect_to_url(short_key: str, db: Session = Depends(database.get_db)):
    db_url = crud.get_url(db, short_key=short_key)
    if db_url is None or db_url.is_active == 0:
        raise HTTPException(status_code=404, detail="URL not found or inactive")
    return {"target_url": db_url.target_url}

# URL 비활성화 엔드포인트
@router.delete("/{short_key}")
def deactivate_url(short_key: str, db: Session = Depends(database.get_db)):
    db_url = crud.deactivate_url(db, short_key=short_key)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"message": "URL successfully deactivated"}
