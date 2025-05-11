# app/auth/api/permission.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth import crud, schemas

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.post("/", response_model=schemas.Permission)
def create_perm(p: schemas.PermissionCreate, db: Session = Depends(get_db)):
    return crud.permission.create_permission(db, p)
