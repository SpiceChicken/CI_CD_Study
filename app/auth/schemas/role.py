from pydantic import BaseModel
from typing import List
from .permission import Permission

class RoleBase(BaseModel):
    name: str
    description: str = None

class RoleCreate(RoleBase):
    permission_ids: List[int] = []

class Role(RoleBase):
    id: int
    permissions: List['Permission'] = []
    class Config:
        orm_mode = True
