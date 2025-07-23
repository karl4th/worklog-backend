from fastapi import APIRouter, Depends, HTTPException
from src.worklog.shifts.schemas import *
from src.worklog.shifts.service import ShiftService
from src.worklog.db.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.config.auth import auth
from src.worklog.rules.permissions import PermissionService


router = APIRouter(prefix="/api/v1/shifts", tags=["⏱️SHIFTS - rotation-cycles"])

@router.post("/", response_model=ShiftResponse)
async def create_shift(shift: CreateShift, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "create_shift"):
        raise HTTPException(status_code=403, detail="User does not have permission to create shifts")
    return await ShiftService(db).create_shift(shift)   

@router.get("/", response_model=ShiftListResponse)
async def get_shifts(db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "get_shifts"):
        raise HTTPException(status_code=403, detail="User does not have permission to get shifts")
    return await ShiftService(db).get_shifts()

@router.get("/{shift_id}", response_model=ShiftResponse)
async def get_shift(shift_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "get_shift"):
        raise HTTPException(status_code=403, detail="User does not have permission to get shifts")
    return await ShiftService(db).get_shift(shift_id)

@router.put("/{shift_id}", response_model=ShiftResponse)
async def update_shift(shift_id: int, shift: UpdateShift, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "update_shift"):
        raise HTTPException(status_code=403, detail="User does not have permission to update shifts")
    return await ShiftService(db).update_shift(shift_id, shift)     

@router.delete("/{shift_id}", response_model=dict)
async def delete_shift(shift_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "delete_shift"):
        raise HTTPException(status_code=403, detail="User does not have permission to delete shifts")
    return await ShiftService(db).delete_shift(shift_id)

@router.get('/update/active/shifts', response_model=bool)
async def update_active_shifts(db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    service = ShiftService(db)
    return await service.update_shift_actives()