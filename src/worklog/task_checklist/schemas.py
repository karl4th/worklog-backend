from pydantic import BaseModel, Field
from datetime import datetime

class UserData(BaseModel):
    id: int = Field(..., description="The id of the user")
    first_name: str = Field(..., description="The first name of the user")
    last_name: str = Field(..., description="The last name of the user")
    middle_name: str = Field(..., description="The middle name of the user")
    position: str = Field(..., description="The position of the user")


class CheckListItemResponse(BaseModel):
    id: int = Field(..., description="The ID of the checklist item")
    checklist_id: int = Field(..., description="The ID of the checklist")
    content: str = Field(..., description="The content of the checklist item")
    is_checked: bool = Field(..., description="Whether the checklist item is checked")
    completed_by: UserData | None = Field(None, description="The user who completed the checklist item")
    created_at: datetime = Field(..., description="The creation date of the checklist item")
    updated_at: datetime = Field(..., description="The update date of the checklist item")

class CheckListWithItemsResponse(BaseModel):
    id: int = Field(..., description="The ID of the checklist")
    task_id: int = Field(..., description="The ID of the task")
    title: str = Field(..., description="The title of the checklist")
    description: str = Field(..., description="The description of the checklist")
    checklist_items: list[CheckListItemResponse] | None

class TaskChecklistListResponse(BaseModel):
    checklists: list[CheckListWithItemsResponse]

class CreateCheckList(BaseModel):
    title: str = Field(..., description="The title of the checklist")
    description: str = Field(..., description="The description of the checklist")

class UpdateCheckList(BaseModel):
    title: str = Field(..., description="The title of the checklist")
    description: str = Field(..., description="The description of the checklist")

class CreateCheckListItem(BaseModel):
    content: str = Field(..., description="The content of the checklist item")
