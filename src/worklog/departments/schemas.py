from pydantic import BaseModel, Field
from datetime import datetime
class CreateDepartment(BaseModel):
    name: str = Field(..., example="РЭМУ")
    description: str = Field(..., example="Ремонтно-эксплуатационное управление")

class UpdateDepartment(BaseModel):
    name: str = Field(..., example="РЭМУ")
    description: str = Field(..., example="Ремонтно-эксплуатационное управление")

class DepartmentResponse(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="РЭМУ")
    description: str = Field(..., example="Ремонтно-эксплуатационное управление")

    total_employees: int = Field(..., example=1)

    created_at: datetime = Field(..., example="2021-01-01 00:00:00")
    updated_at: datetime = Field(..., example="2021-01-01 00:00:00")

    class Config:
        from_attributes = True

class DepartmentList(BaseModel):
    departments: list[DepartmentResponse]
    total_departments: int = Field(..., example=1)
