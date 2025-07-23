from pydantic import BaseModel, Field
from datetime import datetime


class CreateBlock(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="0-0-1")
    description: str = Field(..., min_length=1, max_length=50, example="Восточный блок ")

class UpdateBlock(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="0-0-1")
    description: str = Field(..., min_length=1, max_length=50, example="Восточный блок ")

class BlockResponse(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., min_length=1, max_length=50, example="0-0-1")
    description: str = Field(..., min_length=1, max_length=50, example="Восточный блок ")
 
    total_wells: int = Field(..., example=1)
    active_wells: int = Field(..., example=1)
    inactive_wells: int = Field(..., example=1)

    created_at: datetime = Field(..., example=datetime.now())
    updated_at: datetime = Field(..., example=datetime.now())

    class Config:
        from_attributes = True

class BlockList(BaseModel):
    blocks: list[BlockResponse]
    total_blocks: int = Field(..., example=1)
