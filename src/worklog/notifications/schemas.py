from pydantic import BaseModel, Field
from datetime import datetime

class CreateNotification(BaseModel):
    priority: int = Field(..., description="The priority of the notification")
    title: str = Field(..., description="The title of the notification")
    message: str = Field(..., description="The message of the notification")
    repeat: bool = Field(..., description="The repeat of the notification")


class UpdateNotification(BaseModel):
    priority: int = Field(..., description="The priority of the notification")
    title: str = Field(..., description="The title of the notification")
    message: str = Field(..., description="The message of the notification")
    repeat: bool = Field(..., description="The repeat of the notification")


class NotificationResponse(BaseModel):
    id: int = Field(..., description="The id of the notification")
    priority: int = Field(..., description="The priority of the notification")
    title: str = Field(..., description="The title of the notification")
    message: str = Field(..., description="The message of the notification")
    repeat: bool = Field(..., description="The repeat of the notification")
    user_id: int = Field(..., description="The user id of the notification")
    is_read: bool = Field(..., description="The is read of the notification")
    created_at: datetime = Field(..., description="The created at of the notification")
    updated_at: datetime = Field(..., description="The updated at of the notification")

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int = Field(..., description="The total of the notifications")