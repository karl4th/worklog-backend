from .models import Wells
from src.worklog.blocks.models import Block
from .schema import *
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from typing import Optional

class WellsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_well(self, well: CreateWells, block_id: int) -> WellsResponse:
        try:
            # Check if block exists
            check_block = await self.db.execute(select(Block).where(Block.id == block_id))
            if not check_block.scalar_one_or_none():
                raise HTTPException(status_code=404, detail={"status": "error", "message": "Block not found"})
            
            # Check if well with same name exists in block
            existing_well = await self.db.execute(
                select(Wells).where(Wells.name == well.name, Wells.block_id == block_id)
            )
            if existing_well.scalar_one_or_none():
                raise HTTPException(
                    status_code=400, 
                    detail={"status": "error", "message": "Well with this name already exists in this block"}
                )
            
            new_well = Wells(
                name=well.name,
                status=well.status,
                out=well.out,
                depth=well.depth,
                block_id=block_id
            )
            self.db.add(new_well)
            await self.db.commit()
            await self.db.refresh(new_well)
            return new_well
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})
    
    async def get_wells(self, block_id: int) -> WellsListResponse:
        try:
            wells = await self.db.execute(select(Wells).where(Wells.block_id == block_id))
            wells_list = wells.scalars().all()
            return WellsListResponse(
                wells=wells_list,
                block_id=block_id,
                total=len(wells_list)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})
    
    async def get_well(self, well_id: int) -> WellsResponse:
        try:
            well = await self.db.execute(select(Wells).where(Wells.id == well_id))
            if not well.scalar_one_or_none():
                raise HTTPException(status_code=404, detail={"status": "error", "message": "Well not found"})
            return well.scalar_one()
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})
    
    async def update_well(self, well_id: int, well: UpdateWells) -> WellsResponse:
        try:
            check_well = await self.db.execute(select(Wells).where(Wells.id == well_id))
            well_to_update = check_well.scalar_one_or_none()
            if not well_to_update:
                raise HTTPException(status_code=404, detail={"status": "error", "message": "Well not found"})
            
            # Validate status if provided
            if well.status is not None and well.status not in ["active", "inactive", "maintenance"]:
                raise HTTPException(
                    status_code=400, 
                    detail={"status": "error", "message": "Invalid status value"}
                )
            
            # Update only allowed fields
            update_data = well.model_dump(exclude_unset=True)
            if "block_id" in update_data:
                raise HTTPException(
                    status_code=400, 
                    detail={"status": "error", "message": "Cannot change block_id"}
                )
            
            for field, value in update_data.items():
                setattr(well_to_update, field, value)
            
            await self.db.commit()
            await self.db.refresh(well_to_update)
            return well_to_update
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})
    
    async def delete_well(self, well_id: int) -> dict:
        try:
            well = await self.db.execute(select(Wells).where(Wells.id == well_id))
            well_to_delete = well.scalar_one_or_none()
            if not well_to_delete:
                raise HTTPException(status_code=404, detail={"status": "error", "message": "Well not found"})
            await self.db.delete(well_to_delete)
            await self.db.commit()
            return {"status": "success", "message": "Well deleted successfully"}
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})

