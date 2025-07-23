from .models import Shift
from .schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from typing import List
from src.worklog.auth.models import Users
from sqlalchemy import func
from datetime import datetime

class ShiftService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def __check_in_day(self, start: int, end: int) -> bool:
        day = datetime.today().day
        if day < 1 or day > 31:
            return False

        if start <= end:
            return start <= day < end
        else:
            # Диапазон через границу месяца (например, 21–6)
            return day >= start or day < end

    async def _get_employee_count(self, department_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Users).where(Users.department_id == department_id)
        )
        return result.scalar()

    async def create_shift(self, shift: CreateShift) -> ShiftResponse:
        try: 
            new_shift = Shift(
                name=shift.name,
                start_day=shift.start_day,
                end_day=shift.end_day
            )
            self.db.add(new_shift)
            await self.db.commit() 
            await self.db.refresh(new_shift)
            return ShiftResponse(
                id=new_shift.id,
                name=new_shift.name,
                start_day=new_shift.start_day,
                end_day=new_shift.end_day,
                is_active=new_shift.is_active,
                total_employees=await self._get_employee_count(new_shift.id)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_shift(self, shift_id: int) -> ShiftResponse:
        shift = await self.db.get(Shift, shift_id)
        if not shift:
            raise HTTPException(status_code=404, detail="Shift not found")
        return ShiftResponse(
            id=shift.id,
            name=shift.name,
            start_day=shift.start_day,
            end_day=shift.end_day,
            is_active=self.__check_in_day(shift.start_day, shift.end_day),
            total_employees=await self._get_employee_count(shift.id)
        )
    
    async def get_shifts(self) -> ShiftListResponse:
        shifts = await self.db.execute(select(Shift).order_by(Shift.id))
        shifts = shifts.scalars().all()
        return ShiftListResponse(
            shifts=[ShiftResponse(
                id=shift.id,
                name=shift.name,
                start_day=shift.start_day,
                end_day=shift.end_day,
                is_active=self.__check_in_day(shift.start_day, shift.end_day),
                total_employees=await self._get_employee_count(shift.id)
            ) for shift in shifts],
            total=len(shifts)
        )
    
    async def update_shift(self, shift_id: int, shift: UpdateShift) -> ShiftResponse:   
        db_shift = await self.db.get(Shift, shift_id)
        if not db_shift:
            raise HTTPException(status_code=404, detail="Shift not found")
        for field, value in shift.model_dump().items():
            setattr(db_shift, field, value)
        await self.db.commit()
        await self.db.refresh(db_shift) 
        return ShiftResponse(
            id=db_shift.id,
            name=db_shift.name,
            start_day=db_shift.start_day,
            end_day=db_shift.end_day,
            is_active=db_shift.is_active,
            total_employees=await self._get_employee_count(db_shift.id)
        )
    
    async def delete_shift(self, shift_id: int) -> dict:
        shift = await self.db.get(Shift, shift_id)
        if not shift:
            raise HTTPException(status_code=404, detail="Shift not found")
        await self.db.delete(shift)
        await self.db.commit()
        return {"message": "Shift deleted successfully"}

    async def update_shift_actives(self):
        shifts_db = await self.db.execute(select(Shift))
        result = shifts_db.scalars().all()

        for shift in result:
            is_active = self.__check_in_day(shift.start_day, shift.end_day)
            shift.is_active = is_active

        await self.db.commit()
        await self.db.refresh(shifts_db)

        return True
