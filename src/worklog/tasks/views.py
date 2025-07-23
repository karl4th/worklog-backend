from fastapi import APIRouter, Depends, HTTPException, status
from src.worklog.tasks.schemas import *
from src.worklog.tasks.service import TaskService, TaskShowSerivce
from src.worklog.db.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.config.auth import auth
from src.worklog.rules.permissions import PermissionService

router = APIRouter(prefix="/api/v1/tasks", tags=["🔍TASKS - task-manager"])


@router.post("/", response_model=TaskResponse)
async def create_task(task: CreateTask, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "create_task"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_service = TaskService(db)
    return await task_service.create_new_task_and_assign_me(task, int(current_user["sub"]))

@router.post("/department/{department_id}", response_model=TaskResponse)
async def create_task(task: CreateTask, department_id: int, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "create_task"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_service = TaskService(db)
    task = await task_service.create_new_task_and_assign_me(task, int(current_user["sub"]))
    await task_service.add_new_department_to_task(task.id, department_id)
    return task


@router.get("/my-tasks", response_model=TaskListResponse)
async def get_all_my_tasks(current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "get_all_my_tasks"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_service = TaskService(db)
    return await task_service.get_all_my_tasks(int(current_user["sub"]))

@router.get("/department-tasks", response_model=TaskListResponse)
async def get_all_department_tasks(department_id: int, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    task_service = TaskService(db)
    return await task_service.get_all_tasks_by_department(department_id)

@router.get('/task/show-list')
async def get_list_which_user_can_see(current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    handler = TaskShowSerivce(db)
    return await handler.get_list_which_user_can_see(int(current_user["sub"]))


@router.post('/task/add-user', response_model=TaskResponse)
async def add_user_to_task(task_id: int, user_id: int, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "add_user_to_task"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_service = TaskService(db)
    return await task_service.add_new_user_to_task(task_id, user_id)


@router.post('/task/add-department', response_model=TaskResponse)
async def add_department_to_task(task_id: int, department_id: int, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "add_department_to_task"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_service = TaskService(db)
    return await task_service.add_new_department_to_task(task_id, department_id)


@router.delete('/task/remove/user/{task_id}/{user_id}', response_model=bool)
async def remove_user_from_task(task_id: int, user_id: int, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "remove_user_from_task"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_service = TaskService(db)
    return await task_service.remove_user_from_task(task_id, user_id)   


@router.delete('/task/remove/department/{task_id}/{department_id}', response_model=bool)
async def remove_department_from_task(task_id: int, department_id: int, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "remove_department_from_task"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_service = TaskService(db)
    return await task_service.remove_department_from_task(task_id, department_id)


@router.put('/task/change-status', response_model=TaskResponse)
async def change_task_status(task_id: int, status: str, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "change_task_status"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_service = TaskService(db)
    return await task_service.task_change_status(task_id, status)

@router.put('/task/change/{task_id}', response_model=TaskResponse)
async def change_task_data(task_id: int, data: UpdateTask, current_user: dict= Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    task_service = TaskService(db)
    return await task_service.update_task_data(task_id, data)

@router.get('/task/details/{task_id}', response_model=TaskDetailResponse)
async def get_task_details(task_id: int, current_user: dict = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    permission_service = PermissionService(db)
    if not await permission_service.user_access_control(current_user['sub'], "get_task_details"):
        raise HTTPException(status_code=403, detail="Forbidden")
    task_service = TaskService(db)
    return await task_service.get_task_by_id(task_id)

@router.post('/task/ai/by/get/user/', response_model=TaskListResponse)
async def get_user_tasks(user: GetUserTask, db: AsyncSession = Depends(get_db)):
    service = TaskService(db)

    return await service.get_all_my_tasks_by_ai(int(user.user_id))

@router.post('/task/ai/by/new/task', response_model=TaskResponse)
async def create_task_by_ai(task: CreateTaskByAI, db: AsyncSession = Depends(get_db)):
    service = TaskService(db)
    return await service.create_new_task_and_assign_me_by_ai(task)

@router.post('/task/ai/by/update/task', response_model=TaskResponse)
async def update_task_by_ai(task: UpdateTaskStatusByAI, db: AsyncSession = Depends(get_db)):
    service = TaskService(db)
    return await service.task_change_status_by_ai(task)