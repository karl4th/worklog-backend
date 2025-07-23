from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CreateTask(BaseModel):
    title: str = Field(..., description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    status: str = Field(..., description="The status of the task") # new, in_progress, completed, archived, testing, done
    priority: str = Field(..., description="The priority of the task") # low, medium, high, critical
    due_date: datetime = Field(..., description="The due date of the task", example=datetime.now())

class UpdateTask(BaseModel):
    title: Optional[str] = Field(..., description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    status: Optional[str] = Field(...,description="The status of the task")  # new, in_progress, completed, archived, testing, done
    priority: Optional[str] = Field(..., description="The priority of the task")  # low, medium, high, critical
    due_date: Optional[datetime] = Field(..., description="The due date of the task", example=datetime.now())

class TaskResponse(BaseModel):
    id: int = Field(..., description="The id of the task")
    title: str = Field(..., description="The title of the task")
    status: str = Field(..., description="The status of the task")
    priority: str = Field(..., description="The priority of the task")

    class Config:
        from_attributes = True

class TaskUserResponse(BaseModel):
    id: int = Field(..., description="The id of the user")
    first_name: str = Field(..., description="The first name of the user")
    last_name: str = Field(..., description="The last name of the user")
    middle_name: str = Field(..., description="The middle name of the user")
    position: str = Field(..., description="The position of the user")

class TaskDepartmentResponse(BaseModel):
    id: int = Field(..., description="The id of the department")
    name: str = Field(..., description="The name of the department")


class TaskDetailResponse(BaseModel):
    id: int = Field(..., description="The id of the task")
    title: str = Field(..., description="The title of the task")
    status: str = Field(..., description="The status of the task")
    priority: str = Field(..., description="The priority of the task")
    due_date: datetime = Field(..., description="The due date of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    user_assigned: List[TaskUserResponse]
    departments: List[TaskDepartmentResponse]


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse] = Field(..., description="The list of tasks")
    total: int = Field(..., description="The total number of tasks")

    class Config:
        from_attributes = True


class GetUserTask(BaseModel):
    user_id: int

class CreateTaskByAI(BaseModel):
    user_id: int = Field(..., description="The user id of the task")
    title: str = Field(..., description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    status: str = Field(..., description="The status of the task") # new, in_progress, completed, archived, testing, done
    priority: str = Field(..., description="The priority of the task") # low, medium, high, critical
    due_date: datetime = Field(..., description="The due date of the task", example=datetime.now())

class UpdateTaskStatusByAI(BaseModel):
    task_id: int = Field(..., description="The id of the task")
    status: str = Field(..., description="The status of the task")