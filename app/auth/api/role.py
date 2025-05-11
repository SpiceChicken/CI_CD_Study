# app/auth/api/role.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth import crud, schemas

router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("/", response_model=schemas.Role)
def create_role(r: schemas.RoleCreate, db: Session = Depends(get_db)):
    role = crud.role.create_role(db, r.name, r.description)
    if r.permission_ids:
        role = crud.role.assign_permissions(db, role.id, r.permission_ids)
    return role
