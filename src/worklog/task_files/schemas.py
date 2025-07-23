from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class TaskFileResponse(BaseModel):
    id: int = Field(..., description="The ID of the task file")
    task_id: int = Field(..., description="The ID of the task")
    original_filename: str = Field(..., description="The original filename of the file")
    new_filename: str = Field(..., description="The new filename of the file")
    created_by: int = Field(..., description="The ID of the user who created the file")
    created_at: datetime = Field(..., description="The date and time the file was created")
    updated_at: datetime = Field(..., description="The date and time the file was updated")

class TaskFileList(BaseModel):
    files: List[TaskFileResponse]
    total: int = Field(..., description="The total number of files")

