from pydantic import BaseModel, Field
from datetime import datetime

# ROLES #

class CreateRole(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="user")
    description: str = Field(..., min_length=1, max_length=255, example="Пользователь системы")

class UpdateRole(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="admin")
    description: str = Field(..., min_length=1, max_length=255, example="Администратор системы")

class RoleResponse(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., min_length=1, max_length=50, example="admin")
    description: str = Field(..., min_length=1, max_length=255, example="Администратор системы")

    created_at: datetime = Field(..., example=datetime.now())
    updated_at: datetime = Field(..., example=datetime.now())

class RoleList(BaseModel):
    roles: list[RoleResponse]
    total: int = Field(..., example=1)

class RolePermissionResponse(BaseModel):
    role_id: int = Field(..., example=1)
    permission_id: int = Field(..., example=1)
    
    class Config:
        from_attributes = True

class RolePermissionList(BaseModel):
    data: list[RolePermissionResponse]

class RolePermissionSave(BaseModel):
    permissions: dict[str, list[int]]  # role_id: [permission_ids]

# PERMISSIONS #

class CreatePermission(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="create-user")
    display_name: str = Field(..., min_length=1, max_length=50, example="Создание пользователя")
    page: str = Field(..., example="act")

class UpdatePermission(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="create-user")
    display_name: str = Field(..., min_length=1, max_length=50, example="Создание пользователя")
    page: str = Field(..., example="act")

class PermissionResponse(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., min_length=1, max_length=50, example="create-user")
    display_name: str = Field(..., min_length=1, max_length=50, example="Создание пользователя")
    page: str = Field(..., example="act")

    created_at: datetime = Field(..., example=datetime.now())
    updated_at: datetime = Field(..., example=datetime.now())

    class Config:
        from_attributes = True

class PermissionList(BaseModel):
    permissions: list[PermissionResponse]
    total: int = Field(..., example=1)

