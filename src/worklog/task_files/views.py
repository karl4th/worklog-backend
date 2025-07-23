from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from .service import TaskFilesService
from .schemas import TaskFileResponse, TaskFileList
from src.worklog.db.core import get_db
from src.worklog.config.auth import auth
from src.worklog.rules.permissions import PermissionService

router = APIRouter(prefix="/api/v1/task_files", tags=["🗂️TASK FILES - document-vault"])



@router.get("/{task_id}", response_model=TaskFileList)
async def get_task_files(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(auth.get_user_data_dependency())
):
    """
    Get all files attached to a task.
    
    Args:
        task_id: The ID of the task
        
    Returns:
        TaskFileList containing all files attached to the task
    """
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "get_task_files"):
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        service = TaskFilesService(db)
        result = await service.get_task_files(task_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task files: {str(e)}"
        )


@router.post("/uploads/{task_id}")
async def new_uploaded_file(task_id: int, uploaded_file: UploadFile, db: AsyncSession = Depends(get_db), current_user: dict = Depends(auth.get_user_data_dependency())):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "new_uploaded_file"):
        raise HTTPException(status_code=403, detail="Forbidden")
    handler = TaskFilesService(db)
    result = await handler._save_uploaded_file(uploaded_file)
    task_result = await handler.create_task_file(task_id, result, int(current_user["sub"]))
    return task_result


