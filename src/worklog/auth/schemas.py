from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, example="Бағжан")
    last_name: str = Field(..., min_length=1, max_length=50, example="Карл")
    middle_name: Optional[str] = Field(None, min_length=1, max_length=50, example="Саматұлы")
    phone: str = Field(..., min_length=1, max_length=12, example="+77071234567")
    password: str = Field(..., min_length=8, max_length=256, example="SuperPassword123")
    position: Optional[str] = Field(None, min_length=1, max_length=50, example="Администратор")
    department_id: Optional[int] = Field(None, example=1)
    shift_id: Optional[int] = Field(None, example=1)
    role: int = Field(..., example=1)


class UpdateUser(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, example="Бағжан")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, example="Карл")
    middle_name: Optional[str] = Field(None, min_length=1, max_length=50, example="Саматұлы")
    phone: Optional[str] = Field(None, min_length=1, max_length=12, example="+77071234567")
    password: Optional[str] = Field(None, min_length=8, max_length=256, example="SuperPassword123")
    position: Optional[str] = Field(None, min_length=1, max_length=50, example="Администратор")
    department_id: Optional[int] = Field(None, example=1)
    shift_id: Optional[int] = Field(None, example=1)

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


class UserLogin(BaseModel):
    phone: str = Field(..., min_length=1, max_length=12, example="+77071234567")
    password: str = Field(..., min_length=8, max_length=256, example="SuperPassword123")

