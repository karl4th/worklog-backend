from fastapi import HTTPException

from .schemas import *
from .models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from src.worklog.departments.models import Department
from src.worklog.auth.models import Users
from src.worklog.rules.permissions import PermissionService
from src.worklog.notifications.service import NotificationService
from src.worklog.ai.whatsapp_handler import WhatsappHandler


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.whatsapp_handler = WhatsappHandler()

    async def create_new_task_and_assign_me(self, task: CreateTask, user_id: int) -> TaskResponse:
        try:
            # Check if user exists
            user = await self.db.get(Users, user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            new_task = Tasks(
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                due_date=task.due_date)

            self.db.add(new_task)
            await self.db.flush()

            task_assignee = TaskAssignees(
                task_id=new_task.id,
                user_id=user_id)

            self.db.add(task_assignee)
            await self.db.commit()
            await self.db.refresh(new_task)

            return TaskResponse(
                id=new_task.id,
                title=new_task.title,
                status=new_task.status,
                priority=new_task.priority
            )
        
        except Exception as e:
            await self.db.rollback()
            raise e

    async def create_new_task_and_assign_me_by_ai(self, task: CreateTaskByAI) -> TaskResponse:
        try:
            # Check if user exists
            user = await self.db.get(Users, task.user_id)
            if not user:
                raise ValueError(f"User with id {task.user_id} not found")

            new_task = Tasks(
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                due_date=task.due_date)

            self.db.add(new_task)
            await self.db.flush()

            task_assignee = TaskAssignees(
                task_id=new_task.id,
                user_id=task.user_id)

            self.db.add(task_assignee)
            await self.db.commit()
            await self.db.refresh(new_task)

            return TaskResponse(
                id=new_task.id,
                title=new_task.title,
                status=new_task.status,
                priority=new_task.priority
            )

        except Exception as e:
            await self.db.rollback()
            raise e

    async def create_new_task_without_assign(self,
                                            title: str,
                                            description: str,
                                            status: str,
                                            priority: str,
                                            due_date: str,
                                            user_id: int) -> TaskResponse:
        try:
            new_task = Tasks(
                title=title,
                description=description,
                status=status,
                priority=priority,
                due_date=due_date)
            
            self.db.add(new_task)
            await self.db.flush()

            task_assignee = TaskAssignees(
                task_id=new_task.id,
                user_id=user_id)
            
            self.db.add(task_assignee)
            await self.db.commit()
            await self.db.refresh(new_task)
            return TaskResponse(
                id=new_task.id,
                title=new_task.title,
                status=new_task.status,
                priority=new_task.priority
            )
        except Exception as e:
            await self.db.rollback()
            raise e


    async def add_new_user_to_task(self, task_id: int, user_id: int) -> TaskResponse:
        try:
            # Check if task exists
            task = await self.db.get(Tasks, task_id)
            if not task:
                raise ValueError(f"Task with id {task_id} not found")

            # Check if user exists
            user = await self.db.get(Users, user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            # Check if assignment already exists
            existing = await self.db.execute(
                select(TaskAssignees).where(
                    and_(
                        TaskAssignees.task_id == task_id,
                        TaskAssignees.user_id == user_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"User {user_id} is already assigned to task {task_id}")

            task_assignee = TaskAssignees(
                task_id=task_id,
                user_id=user_id)

            self.db.add(task_assignee)
            result = await self.whatsapp_handler.send_message(f"Вы были назначены на задачу '{task.title}'! \n\n https://ortalyk.worklog.kz/tasks/{task.id}", user.chat_id_whatsapp)
            await self.db.commit()
            await self.db.refresh(task)
            return TaskResponse(
                id=task.id,
                title=task.title,
                status=task.status,
                priority=task.priority
            )
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Invalid task_id or user_id")
        except Exception as e:
            await self.db.rollback()
            raise e

    async def add_new_department_to_task(self, task_id: int, department_id: int) -> TaskResponse:
        try:
            # Check if task exists
            task = await self.db.get(Tasks, task_id)
            if not task:
                raise ValueError(f"Task with id {task_id} not found")

            # Check if department exists
            department = await self.db.get(Department, department_id)
            if not department:
                raise ValueError(f"Department with id {department_id} not found")

            # Check if department assignment already exists
            existing = await self.db.execute(
                select(TaskDepartments).where(
                    and_(
                        TaskDepartments.task_id == task_id,
                        TaskDepartments.department_id == department_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Department {department_id} is already assigned to task {task_id}")

            task_department = TaskDepartments(
                task_id=task_id,
                department_id=department_id)
            self.db.add(task_department)
            await self.db.commit()
            await self.db.refresh(task)

            return TaskResponse(
                id=task.id,
                title=task.title,
                status=task.status,
                priority=task.priority
            )
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Invalid task_id or department_id")
        except Exception as e:
            await self.db.rollback()
            raise e

    async def update_task_data(self, task_id: int, data: UpdateTask) -> TaskResponse:
        try:
            query = select(Tasks).where(Tasks.id == task_id)
            result = await self.db.execute(query)
            task = result.scalars().first()

            if not task:
                raise ValueError(f"Task with id {task_id} not found")

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(task, field, value)

            await self.db.commit()
            await self.db.refresh(task)
            return TaskResponse(
                id=task.id,
                title=task.title,
                status=task.status,
                priority=task.priority
            )
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


    async def remove_user_from_task(self, task_id: int, user_id: int) -> bool:
        try:            
            task = await self.db.get(Tasks, task_id)
            user = await self.db.get(Users, user_id)
            task_assignee = await self.db.execute(select(TaskAssignees).where(TaskAssignees.task_id == task_id, TaskAssignees.user_id == user_id))
            res = task_assignee.scalars().first()
            if not res:
                return True

            await self.db.delete(res)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise e
        
    async def remove_department_from_task(self, task_id: int, department_id: int) -> bool:
        try:

            task_department = await self.db.execute(select(TaskDepartments).where(TaskDepartments.task_id == task_id, TaskDepartments.department_id == department_id))
            res = task_department.scalars().first()
            if not res:
                raise ValueError(f"Department with id {department_id} is not assigned to task with id {task_id}")

            await self.db.delete(res)
            await self.db.commit()
            return True
        except Exception as e:  
            await self.db.rollback()
            raise e
    

    async def get_all_my_tasks(self, user_id: int) -> TaskListResponse:
        try:
            # Check if user exists
            user = await self.db.get(Users, user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            query = select(Tasks).join(
                TaskAssignees,
                Tasks.id == TaskAssignees.task_id
            ).where(TaskAssignees.user_id == user_id)
            
            result = await self.db.execute(query)
            tasks = result.scalars().all()
            return TaskListResponse(tasks=[TaskResponse(id=task.id, title=task.title, status=task.status, priority=task.priority) for task in tasks], total=len(tasks))
        except Exception as e:
            raise e

    async def get_all_tasks_by_department(self, department_id: int) -> TaskListResponse:
        try:
            # Check if department exists
            department = await self.db.get(Department, department_id)
            if not department:
                raise ValueError(f"Department with id {department_id} not found")

            query = select(Tasks).join(
                TaskDepartments,
                Tasks.id == TaskDepartments.task_id
            ).where(TaskDepartments.department_id == department_id)
            
            result = await self.db.execute(query)
            tasks = result.scalars().all()
            return TaskListResponse(tasks=[TaskResponse(id=task.id, title=task.title, status=task.status, priority=task.priority) for task in tasks], total=len(tasks))
        except Exception as e:
            raise e

    async def task_change_status(self, task_id: int, status: str) -> TaskResponse:
        try:
            task = await self.db.get(Tasks, task_id)
            if not task:
                raise ValueError(f"Task with id {task_id} not found")
            
            task.status = status
            await self.db.commit()
            await self.db.refresh(task)
            return TaskResponse(id=task.id, title=task.title, status=task.status, priority=task.priority)
        except Exception as e:
            await self.db.rollback()
            raise e
            

    async def get_task_by_id(self, task_id: int) -> TaskDetailResponse:
        try:
            task = await self.db.get(Tasks, task_id)
            if not task:
                raise ValueError(f"Task with id {task_id} not found")
            
            # Get assignees for this task
            assignees_query = select(TaskAssignees).where(TaskAssignees.task_id == task_id)
            assignees_result = await self.db.execute(assignees_query)
            assignees = assignees_result.scalars().all()
            
            # Get departments for this task
            departments_query = select(TaskDepartments).where(TaskDepartments.task_id == task_id)
            departments_result = await self.db.execute(departments_query)
            departments = departments_result.scalars().all()
            
            # Get user details for assignees
            user_assigned = []
            for assignee in assignees:
                user = await self.db.get(Users, assignee.user_id)
                if user:
                    user_assigned.append(TaskUserResponse(
                        id=user.id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        middle_name=user.middle_name,
                        position=user.position
                    ))
            
            # Get department details
            department_details = []
            for dept in departments:
                department = await self.db.get(Department, dept.department_id)
                if department:
                    department_details.append(TaskDepartmentResponse(
                        id=department.id,
                        name=department.name
                    ))
            
            return TaskDetailResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                due_date=task.due_date,
                user_assigned=user_assigned,
                departments=department_details
            )
        except Exception as e:
            raise e

    async def task_change_status_by_ai(self, task_data: UpdateTaskStatusByAI):
        try:
            task = await self.db.get(Tasks, task_data.task_id)
            if not task:
                raise ValueError(f"Task with id {task_data.task_id} not found")

            task.status = task_data.status
            await self.db.commit()
            await self.db.refresh(task)
            return TaskResponse(id=task.id, title=task.title, status=task.status, priority=task.priority)
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_all_my_tasks_by_ai(self, user_id: int) -> TaskListResponse:
        try:
            # Check if user exists
            user = await self.db.get(Users, user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            allowed_statuses = ["new", "in_progress", "testing", "done"]

            query = select(Tasks).join(
                TaskAssignees,
                Tasks.id == TaskAssignees.task_id
            ).where(
                and_(
                    TaskAssignees.user_id == user_id,
                    Tasks.status.in_(allowed_statuses)
                )
            )

            result = await self.db.execute(query)
            tasks = result.scalars().all()

            return TaskListResponse(
                tasks=[
                    TaskResponse(
                        id=task.id,
                        title=task.title,
                        status=task.status,
                        priority=task.priority
                    ) for task in tasks
                ],
                total=len(tasks)
            )
        except Exception as e:
            raise e


class TaskShowSerivce:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list_which_user_can_see(self, user_id: int) -> TaskListResponse:
        dep_list = []
        total = 0
    
        if await PermissionService(self.db).user_access_control(user_id, "get_all_my_tasks"):
            db_user = await self.db.get(Users, user_id)
            dep_list.append({
                "id": None,
                "name": "my_tasks",
                "display_name": f'{db_user.first_name} {db_user.last_name}'
            })
            department_db = await self.db.execute(select(Department).where(Department.id == db_user.department_id))
            department_db = department_db.scalars().first()
            if department_db:
                dep_list.append({
                    "id": department_db.id,
                    "name": department_db.name,
                    "display_name": department_db.name
                }) 
                total += 1
            total += 1

        if await PermissionService(self.db).user_access_control(user_id, "show_all_department_tasks"):
            db_departments = await self.db.execute(select(Department))
            for dep in db_departments.scalars().all():
                dep_list.append({
                    "id": dep.id,
                    "name": dep.name,
                    "display_name": dep.name
                })
                total += 1
        
        return {"list": dep_list, "total": total}