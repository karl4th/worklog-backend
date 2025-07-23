from pydantic import BaseModel, Field
from typing import Optional, List


class CreateWells(BaseModel):
    name: str = Field(..., description="The name of the well", example="Well 1")
    status: str = Field(..., description="The status of the well", example="active")
    out: bool = Field(..., description="Whether the well is out", example=False)
    depth: Optional[float] = None

class UpdateWells(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    out: Optional[bool] = None
    depth: Optional[float] = None


class WellsResponse(BaseModel):
    id: int
    name: str
    status: str
    out: bool
    depth: Optional[float] = None
    block_id: int

    class Config:
        from_attributes = True

class WellsListResponse(BaseModel):
    wells: List[WellsResponse]
    block_id: int
    total: int

    class Config:
        from_attributes = True

