from sqlalchemy.orm import Session
from app.auth.crud import permission, role

def init_rbac_data(db: Session):
    # 1) 권한 생성
    perms = [
        {"name": "url.create", "description": "단축 URL 생성"},
        {"name": "url.view",   "description": "단축 URL 조회"},
        {"name": "url.delete", "description": "단축 URL 삭제"},
    ]
    created = [permission.create_permission(db, p) for p in perms]

    # 2) 역할 생성
    role_admin    = role.create_role(db, "admin", "전체 권한")
    role_operator = role.create_role(db, "operator", "읽기/생성 권한")

    # 3) 역할에 권한 할당
    role.assign_permissions(db, role_admin.id,    [p.id for p in created])
    role.assign_permissions(db, role_operator.id, [p.id for p in created if p.name!="url.delete"])
