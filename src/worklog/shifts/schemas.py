from pydantic import BaseModel, Field


class CreateShift(BaseModel):
    name: str = Field(..., description="The name of the shift", example="Вахта А")
    start_day: int = Field(..., description="The start day of the shift", example=1)
    end_day: int = Field(..., description="The end day of the shift", example=16)

class UpdateShift(BaseModel):
    name: str = Field(..., description="The name of the shift", example="Вахта А")
    start_day: int = Field(..., description="The start day of the shift", example=1)
    end_day: int = Field(..., description="The end day of the shift", example=16)

class ShiftResponse(BaseModel):
    id: int = Field(..., description="The id of the shift", example=1)
    name: str = Field(..., description="The name of the shift", example="Вахта А")
    start_day: int = Field(..., description="The start day of the shift", example=1)
    end_day: int = Field(..., description="The end day of the shift", example=16)
    is_active: bool = Field(..., description="The active status of the shift", example=True)

    total_employees: int = Field(..., description="The total number of employees", example=1)

    class Config:
        from_attributes = True

class ShiftListResponse(BaseModel):
    shifts: list[ShiftResponse]
    total: int = Field(..., description="The total number of shifts", example=1)
    








