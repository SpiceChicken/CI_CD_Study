from sqlalchemy.orm import Session
from ..models.permission import Permission
from ..schemas.permission import PermissionCreate

def create_permission(db: Session, p: PermissionCreate):
    perm = Permission(**p.dict())
    db.add(perm); db.commit(); db.refresh(perm)
    return perm
