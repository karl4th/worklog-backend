from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.blocks.schemas import *
from src.worklog.blocks.service import BlockService
from src.worklog.rules.permissions import PermissionService
from src.worklog.config.auth import auth
from src.worklog.db.core import get_db


router = APIRouter(prefix="/api/v1/blocks", tags=["🧱BLOCKS - building-blocks"])


@router.post("/", response_model=BlockResponse)
async def create_block(block: CreateBlock, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(user_data['sub'], "create_block"):
        raise HTTPException(status_code=403, detail="User does not have permission to create block")
    return await BlockService(db).create_block(block)

@router.get("/", response_model=BlockList)
async def get_blocks(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(user_data['sub'], "get_blocks"):
        raise HTTPException(status_code=403, detail="User does not have permission to get blocks")
    return await BlockService(db).get_blocks()

@router.get("/{block_id}", response_model=BlockResponse)
async def get_block(block_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(user_data['sub'], "get_block"):
        raise HTTPException(status_code=403, detail="User does not have permission to get block")
    return await BlockService(db).get_block(block_id)

@router.put("/{block_id}", response_model=BlockResponse)
async def update_block(block_id: int, block: UpdateBlock, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(user_data['sub'], "update_block"):
        raise HTTPException(status_code=403, detail="User does not have permission to update block")
    return await BlockService(db).update_block(block_id, block)

@router.delete("/{block_id}", response_model=bool)
async def delete_block(block_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(user_data['sub'], "delete_block"):
        raise HTTPException(status_code=403, detail="User does not have permission to delete block")
    return await BlockService(db).delete_block(block_id)















