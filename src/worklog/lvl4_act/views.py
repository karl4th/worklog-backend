from fastapi import APIRouter, Depends, HTTPException
from src.worklog.lvl4_act.service import ActService
from src.worklog.lvl4_act.schemas import *
from src.worklog.db.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.rules.permissions import PermissionService
from src.worklog.config.auth import auth


router = APIRouter(prefix="/api/v1/acts", tags=["acts"])

@router.post("/", response_model=ActResp)
async def create_act(act: ActCreate, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "create_act"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.create_act(act)
    return result

@router.get("/", response_model=ActListResp)
async def get_all_acts(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "get_all_act"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.get_all_acts()
    return result

@router.post("/whom", response_model=dict)
async def create_act_whom(whom: ActWhomCreate, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "create_act_whom"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.create_act_whom(whom)
    return result

@router.post("/from", response_model=dict)
async def create_act_from(from_whom: ActFromCreate, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "create_act_from"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.create_act_from(from_whom)
    return result

@router.delete("/whom", response_model=dict)
async def delete_act_whom(act_id: int, user_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "delete_act_whom"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.delete_act_whom(act_id, user_id)
    return result

@router.delete("/from", response_model=dict)
async def delete_act_from(act_id: int, user_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "delete_act_from"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.delete_act_from(act_id, user_id)
    return result

@router.post("/items", response_model=dict)
async def create_act_item(item: ActItemsCreate, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "create_act_item"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.create_act_item(item)
    return result

@router.delete("/items/{item_id}", response_model=dict)
async def delete_act_item(item_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "delete_act_item"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.delete_act_item(item_id)
    return result

@router.put("/items/{item_id}", response_model=dict)
async def update_act_item(item_id: int, item: ActItemsCreate, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "update_act_item"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.update_act_item(item_id, item)
    return result   

@router.get("/{act_id}", response_model=ActDetails)
async def get_act_by_id(act_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "get_act_by_id"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.get_act_by_id(act_id)
    return result

@router.put("/{act_id}", response_model=ActResp)
async def update_act(act_id: int, act: ActUpdate, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "update_act"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.update_act(act_id, act)
    return result

@router.delete("/{act_id}", response_model=dict)
async def delete_act(act_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "delete_act"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.delete_act(act_id)
    return result

@router.get("/{act_id}/report", response_model=ActReportList)
async def get_act_report(act_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(user_data['sub']), "get_act_report"):
        raise HTTPException(status_code=403, detail="Forbidden")
    service = ActService(db)
    result = await service.get_act_report(act_id)
    return result
















