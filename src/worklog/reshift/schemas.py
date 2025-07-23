from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class CreateUserShifts(BaseModel):
    first_user_id: int
    second_user_id: int


class ReshiftCreate(BaseModel):
    user_id: int = Field(..., example=123)
    done: str = Field(...)
    todo: str = Field(...)

class User(BaseModel):
    id: int = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    middle_name: str = Field(...)
    position: str = Field(...)

class ReportResponse(BaseModel):
    id: int = Field(...)
    done: str = Field(...)
    todo: str = Field(...)
    user: User
    created_at: datetime = Field(...)

    class Config:
        from_attributes = True

class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total: int = Field(...)