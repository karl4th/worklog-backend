from pydantic import BaseModel
from typing import Optional
class BaseUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    position: str

class UserList(BaseModel):
    users: list[BaseUser]
    total_users: int

class RoleUser(BaseModel):
    id: int
    name: Optional[str] = None

class DepartmentUser(BaseModel):
    id: int
    display_name: str


class ShiftUser(BaseModel):
    id: int
    display_name: str


class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: str
    position: Optional[str] = None
    department: Optional[DepartmentUser] = None
    shift: Optional[ShiftUser] = None
    role: Optional[RoleUser] = None
    is_superuser: bool

class UserServiceBase(BaseModel):
    users: list[UserRead]
    total_users: int
