from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .service import RuleService
from .schemas import *
from src.worklog.config.auth import auth
from src.worklog.db.core import get_db
from .permissions import PermissionService


########################################################
# ROLES
########################################################

role_router = APIRouter(prefix="/api/v1/rules", tags=["📜RULES - access-fortress"])

@role_router.post("/roles", response_model=RoleResponse)
async def create_role(role: CreateRole, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "create_role"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).create_role(role)

@role_router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: int, role: UpdateRole, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "update_role"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).update_role(role_id, role)

@role_router.delete("/roles/{role_id}", response_model=bool)
async def delete_role(role_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "delete_role"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).delete_role(role_id)

@role_router.get("/roles", response_model=RoleList)
async def get_roles(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "get_roles"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).get_roles()

@role_router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "get_role"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).get_role(role_id)


@role_router.get("/role-permissions", response_model=RolePermissionList)
async def get_role_permissions(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "get_role_permissions"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).get_role_permissions()

@role_router.post("/role-permissions", response_model=bool)
async def save_role_permissions(
    permissions: RolePermissionSave,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "save_role_permissions"):
        raise HTTPException(
            status_code=403,
            detail={
                "status": "error",
                "code": "access_denied",
                "message": "Access denied"
            }
        )
    return await RuleService(db).save_role_permissions(permissions.permissions)

########################################################
# PERMISSIONS
########################################################

permission_router = APIRouter(prefix="/api/v1/rules", tags=["🔑PERMISSIONS - access-guardian"])

@permission_router.post("/permission", response_model=PermissionResponse)
async def create_permission(permission: CreatePermission, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "create_permission"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).create_permission(permission)

@permission_router.post("/permissions", response_model=PermissionList)
async def create_permissions(permissions: list[CreatePermission], user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "create_permissions"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).create_permissions(permissions)

@permission_router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(permission_id: int, permission: UpdatePermission, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "update_permission"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).update_permission(permission_id, permission)

@permission_router.delete("/permissions/{permission_id}", response_model=bool)
async def delete_permission(permission_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "delete_permission"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).delete_permission(permission_id)

@permission_router.get("/permissions", response_model=PermissionList)
async def get_permissions(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "get_permissions"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).get_permissions()

@permission_router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(permission_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    if not await access_control.user_access_control(int(user_data['sub']), "get_permission"):
        raise HTTPException(status_code=403, detail={"status": "error", "code": "access_denied", "message": "Access denied"})
    return await RuleService(db).get_permission(permission_id)


@permission_router.get("/check-permission/{permission}", response_model=dict)
async def check_permission(permission: str, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    access_control = PermissionService(db)
    data = await access_control.user_access_control(int(user_data['sub']), permission)
    return {"has_permission": data}

