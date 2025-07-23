from fastapi import APIRouter, Depends, HTTPException
from .schemas import *
from src.worklog.config.auth import auth
from src.worklog.rules.permissions import PermissionService
from src.worklog.db.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .service import NotificationService    


router = APIRouter(prefix="/api/v1/notifications", tags=["📨NOTIFICATIONS - alert-center"])


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(user_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    ...
