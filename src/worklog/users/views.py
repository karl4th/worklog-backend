from fastapi import APIRouter, Depends, HTTPException
from src.worklog.users.service import UserService
from src.worklog.db.core import get_db
from src.worklog.users.schemas import * 
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.config.auth import auth
from src.worklog.rules.permissions import PermissionService

router = APIRouter(prefix="/api/v1/users", tags=["USERS - users"])

@router.get("/list", response_model=UserList)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    return await user_service.get_users(skip, limit)

@router.get("/list/list", response_model=UserServiceBase)
async def get_user(
    current_user: dict = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "get_user_list"):
        raise HTTPException(status_code=403, detail="Forbidden")
    user_service = UserService(db)
    return await user_service.get_user_profiles()
    
