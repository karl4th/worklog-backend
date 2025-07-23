from .schemas import *
from .models import Block
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from typing import List
from src.worklog.wells.models import Wells


class BlockService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_block_out_wells(self, block_id: int) -> List[Wells]:
        wells = await self.db.execute(select(Wells).where(Wells.block_id == block_id, Wells.out == True))
        wells = wells.scalars().all()
        return len(wells)
    
    async def _get_block_total_wells(self, block_id: int) -> int:
        wells = await self.db.execute(select(Wells).where(Wells.block_id == block_id))
        wells = wells.scalars().all()
        return len(wells)
    
    async def _get_block_in_wells(self, block_id: int) -> int:
        wells = await self.db.execute(select(Wells).where(Wells.block_id == block_id, Wells.out == False))
        wells = wells.scalars().all()
        return len(wells)
    
    async def _get_block_active_wells(self, block_id: int) -> List[Wells]:
        wells = await self.db.execute(select(Wells).where(Wells.block_id == block_id, Wells.out == False))
        wells = wells.scalars().all()
        return len(wells)
    
    async def _get_block_inactive_wells(self, block_id: int) -> List[Wells]:
        wells = await self.db.execute(select(Wells).where(Wells.block_id == block_id, Wells.out == False))
        wells = wells.scalars().all()
        return len(wells)
    

    
    async def create_block(self, block: CreateBlock) -> BlockResponse:
        block = Block(**block.model_dump())
        self.db.add(block)
        await self.db.commit()
        await self.db.refresh(block)
        
        # Get well counts
        total_wells = await self._get_block_total_wells(block.id)
        active_wells = await self._get_block_in_wells(block.id)
        inactive_wells = await self._get_block_out_wells(block.id)
        
        return BlockResponse(
            id=block.id,
            name=block.name,
            description=block.description,
            total_wells=total_wells,
            active_wells=active_wells,
            inactive_wells=inactive_wells,
            created_at=block.created_at,
            updated_at=block.updated_at
        )
    
    async def get_block(self, block_id: int) -> BlockResponse:
        block = await self.db.get(Block, block_id)
        if not block:
            raise HTTPException(status_code=404, detail="Block not found")
            
        # Get well counts
        total_wells = await self._get_block_total_wells(block.id)
        active_wells = await self._get_block_in_wells(block.id)
        inactive_wells = await self._get_block_out_wells(block.id)
        
        return BlockResponse(
            id=block.id,
            name=block.name,
            description=block.description,
            total_wells=total_wells,
            active_wells=active_wells,
            inactive_wells=inactive_wells,
            created_at=block.created_at,
            updated_at=block.updated_at
        )
    
    async def get_blocks(self) -> BlockList:
        blocks = await self.db.execute(select(Block))
        blocks = blocks.scalars().all()
        total = len(blocks)
        
        block_responses = []
        for block in blocks:
            # Get well counts for each block
            total_wells = await self._get_block_total_wells(block.id)
            active_wells = await self._get_block_in_wells(block.id)
            inactive_wells = await self._get_block_out_wells(block.id)
            
            block_responses.append(BlockResponse(
                id=block.id,
                name=block.name,
                description=block.description,
                total_wells=total_wells,
                active_wells=active_wells,
                inactive_wells=inactive_wells,
                created_at=block.created_at,
                updated_at=block.updated_at
            ))
            
        return BlockList(blocks=block_responses, total_blocks=total)
    
    async def update_block(self, block_id: int, block: UpdateBlock) -> BlockResponse:
        db_block = await self.db.get(Block, block_id)
        if not db_block:
            raise HTTPException(status_code=404, detail="Block not found")
        
        # Update only provided fields
        update_data = block.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_block, field, value)
            
        await self.db.commit()
        await self.db.refresh(db_block)
        
        # Get well counts
        total_wells = await self._get_block_total_wells(db_block.id)
        active_wells = await self._get_block_in_wells(db_block.id)
        inactive_wells = await self._get_block_out_wells(db_block.id)
        
        return BlockResponse(
            id=db_block.id,
            name=db_block.name,
            description=db_block.description,
            total_wells=total_wells,
            active_wells=active_wells,
            inactive_wells=inactive_wells,
            created_at=db_block.created_at,
            updated_at=db_block.updated_at
        )
    
    async def delete_block(self, block_id: int) -> bool:
        block = await self.db.get(Block, block_id)
        if not block:
            raise HTTPException(status_code=404, detail="Block not found")
        await self.db.delete(block)
        await self.db.commit()
        return True
