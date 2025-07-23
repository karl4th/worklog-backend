from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import *
from .service import TaskChecklistService
from src.worklog.db.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.rules.permissions import PermissionService
from src.worklog.config.auth import auth


router = APIRouter(prefix="/api/v1/task-checklist", tags=["🔍TASK CHECKLIST - task-checklist-manager"])

#TODO: ADD PERMISSION CHECKS

@router.post("/", response_model=CheckListWithItemsResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new checklist for a task",
             description="Creates a new checklist associated with a specific task. The checklist will be empty initially.")
async def create_checklist(
    task_id: int,
    checklist: CreateCheckList, 
    current_user: dict = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)
):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "create_checklist"):
        raise HTTPException(status_code=403, detail="Forbidden")
    checklist_service = TaskChecklistService(db)
    return await checklist_service.create_checklist(checklist, int(current_user["sub"]), task_id)

@router.get("/task/{task_id}", response_model=TaskChecklistListResponse,
            summary="Get all checklists for a task",
            description="Retrieves all checklists associated with a specific task, including their items.")
async def get_task_checklists(
    task_id: int,
    current_user: dict = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)
):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "get_task_checklists"):
        raise HTTPException(status_code=403, detail="Forbidden")
    checklist_service = TaskChecklistService(db)
    return await checklist_service.get_task_checklists(task_id)

@router.get("/{checklist_id}", response_model=CheckListWithItemsResponse,
            summary="Get a specific checklist by ID",
            description="Retrieves a specific checklist by its ID, including all its items.")
async def get_checklist(
    checklist_id: int, 
    current_user: dict = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)
):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "get_checklist"):
        raise HTTPException(status_code=403, detail="Forbidden")
    checklist_service = TaskChecklistService(db)
    return await checklist_service.get_checklist_by_id(checklist_id)

@router.put("/{checklist_id}")
async def update_checklist(data: UpdateCheckList, checklist_id: int, db: AsyncSession = Depends(get_db)):
    service_service = TaskChecklistService(db)
    return await service_service.update_checklist_data(checklist_id, data)

@router.post("/{checklist_id}/items", response_model=CheckListItemResponse, status_code=status.HTTP_201_CREATED,
             summary="Add an item to a checklist",
             description="Adds a new item to an existing checklist.")
async def create_checklist_item(
    checklist_id: int, 
    item: CreateCheckListItem, 
    current_user: dict = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)
):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "create_checklist_item"):
        raise HTTPException(status_code=403, detail="Forbidden")
    checklist_service = TaskChecklistService(db)
    return await checklist_service.create_checklist_item(checklist_id, item)

@router.put("/{checklist_id}/items/{item_id}", response_model=CheckListItemResponse,
            summary="Update a checklist item's status",
            description="Updates the checked status of a specific item in a checklist.")
async def update_checklist_item(
    checklist_id: int, 
    item_id: int, 
    is_checked: bool, 
    current_user: dict = Depends(auth.get_user_data_dependency()), 
    db: AsyncSession = Depends(get_db)
):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "update_checklist_item"):
        raise HTTPException(status_code=403, detail="Forbidden")
    checklist_service = TaskChecklistService(db)
    return await checklist_service.update_checklist_item(int(current_user["sub"]), checklist_id, item_id, is_checked)


@router.delete('/checklists/{checklist_item_id}')
async def delete_checklist_item(checklist_item_id: int, db: AsyncSession = Depends(get_db)):
    service_service = TaskChecklistService(db)
    return await service_service.delete_checklist_item(checklist_item_id)






