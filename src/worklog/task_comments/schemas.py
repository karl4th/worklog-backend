from pydantic import BaseModel, Field
from datetime import datetime


class UserData(BaseModel):
    id: int = Field(..., description="The id of the user")
    first_name: str = Field(..., description="The first name of the user")
    last_name: str = Field(..., description="The last name of the user")
    middle_name: str = Field(..., description="The middle name of the user")
    position: str = Field(..., description="The position of the user")


class TaskCommentResponse(BaseModel):
    id: int = Field(..., description="The id of the task comment")
    content: str = Field(..., description="The content of the task comment")
    user: UserData = Field(..., description="The user who created the task comment")
    created_at: datetime = Field(..., description="The date and time the task comment was created")
    updated_at: datetime = Field(..., description="The date and time the task comment was updated")

class TaskCommentListResponse(BaseModel):
    comments: list[TaskCommentResponse] = Field(..., description="The list of task comments")
    total: int = Field(..., description="The total number of task comments")

class CreateTaskComment(BaseModel):
    content: str = Field(..., description="The content of the task comment")