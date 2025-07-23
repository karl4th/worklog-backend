from fastapi import APIRouter, Depends, HTTPException
from .schemas import *
from .service import *
from src.worklog.db.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.config.auth import auth
from src.worklog.rules.permissions import PermissionService


router = APIRouter(prefix="/api/v1/task-comments", tags=["💬TASK COMMENTS - task-comment-manager"])
#TODO: ADD PERMISSION CHECKS

@router.post("/", response_model=TaskCommentResponse)
async def create_task_comment(task_id: int, comment: CreateTaskComment, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "create_task_comment"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_comment_service = TaskCommentService(db)
    return await task_comment_service.create_task_comment(task_id, int(current_user["sub"]), comment)    

@router.get("/", response_model=TaskCommentListResponse)
async def get_task_comments(task_id: int, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "get_task_comments"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_comment_service = TaskCommentService(db)
    return await task_comment_service.get_task_comments(task_id)
