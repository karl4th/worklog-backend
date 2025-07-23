from fastapi import APIRouter, Depends, HTTPException
from .schemas import *
from src.worklog.config.auth import auth
from src.worklog.rules.permissions import PermissionService
from src.worklog.db.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .service import DepartmentService

router = APIRouter(prefix="/api/v1/departments", tags=["🏢DEPARTMENTS - org-divisions"])


@router.post("/", response_model=DepartmentResponse)
async def create_department(department: CreateDepartment, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data["sub"]), "create_department"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = DepartmentService(db)
    return await service.create_department(department)

@router.get("/", response_model=DepartmentList)
async def get_departments(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data["sub"]), "read_department"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = DepartmentService(db)
    return await service.get_departments()

@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data["sub"]), "read_department"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = DepartmentService(db)
    return await service.get_department(department_id)

@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(department_id: int, department: UpdateDepartment, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data["sub"]), "update_department"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = DepartmentService(db)
    return await service.update_department(department_id, department)

@router.delete("/{department_id}")
async def delete_department(department_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data["sub"]), "delete_department"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = DepartmentService(db)
    return await service.delete_department(department_id)





