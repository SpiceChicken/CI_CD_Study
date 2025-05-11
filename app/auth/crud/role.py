from sqlalchemy.orm import Session
from ..models.role import Role
from ..models.permission import Permission

def create_role(db: Session, name: str, desc: str):
    r = Role(name=name, description=desc)
    db.add(r); db.commit(); db.refresh(r)
    return r

def assign_permissions(db: Session, role_id: int, perm_ids: list[int]):
    role = db.get(Role, role_id)
    perms = db.query(Permission).filter(Permission.id.in_(perm_ids)).all()
    role.permissions = perms
    db.commit(); db.refresh(role)
    return role
