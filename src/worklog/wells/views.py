from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.wells.service import WellsService
from src.worklog.wells.schema import *
from src.worklog.db.core import get_db
from src.worklog.config.auth import auth
from src.worklog.rules.permissions import PermissionService

router = APIRouter(prefix="/api/v1/wells", tags=["💦WELLS - drilling-wells"])

@router.post("/", response_model=WellsResponse)
async def create_well(well: CreateWells, block_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "create_well"):
        raise HTTPException(status_code=403, detail="User does not have permission to create wells")
    return await WellsService(db).create_well(well, block_id)

@router.get("/", response_model=WellsListResponse)
async def get_wells(block_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "get_wells"):
        raise HTTPException(status_code=403, detail="User does not have permission to get wells")
    return await WellsService(db).get_wells(block_id)

@router.get("/{well_id}", response_model=WellsResponse)
async def get_well(well_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "get_well"):
        raise HTTPException(status_code=403, detail="User does not have permission to get wells")
    return await WellsService(db).get_well(well_id) 

@router.put("/{well_id}", response_model=WellsResponse)
async def update_well(well_id: int, well: UpdateWells, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "update_well"):
        raise HTTPException(status_code=403, detail="User does not have permission to update wells")
    return await WellsService(db).update_well(well_id, well)    

@router.delete("/{well_id}", response_model=dict)
async def delete_well(well_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(int(current_user['sub']), "delete_well"):
        raise HTTPException(status_code=403, detail="User does not have permission to delete wells")
    return await WellsService(db).delete_well(well_id)  



