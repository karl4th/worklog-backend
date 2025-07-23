from .schemas import *
from .models import *
from src.worklog.db.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends
from sqlalchemy import select, func
from src.worklog.auth.models import Users

class DepartmentService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def _get_employee_count(self, department_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Users).where(Users.department_id == department_id)
        )
        return result.scalar()

    async def create_department(self, department: CreateDepartment) -> DepartmentResponse:
        try: 
            new_department = Department(
                name=department.name,
                description=department.description
            )
            self.db.add(new_department)
            await self.db.commit()
            await self.db.refresh(new_department)
            total_employees = await self._get_employee_count(new_department.id)
            return DepartmentResponse(
                id=new_department.id,
                name=new_department.name,
                description=new_department.description,
                total_employees=total_employees,
                created_at=new_department.created_at,
                updated_at=new_department.updated_at
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_departments(self) -> DepartmentList:
        departments = await self.db.execute(select(Department))
        departments = departments.scalars().all()
        return DepartmentList(
            departments=[DepartmentResponse(
                id=department.id,
                name=department.name,
                description=department.description,
                total_employees=await self._get_employee_count(department.id),
                created_at=department.created_at,
                updated_at=department.updated_at
            ) for department in departments],
            total_departments=len(departments)
        )

    async def get_department(self, department_id: int) -> DepartmentResponse:
        department = await self.db.get(Department, department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        total_employees = await self._get_employee_count(department_id)
        return DepartmentResponse(
            id=department.id,
            name=department.name,
            description=department.description,
            total_employees=total_employees,
            created_at=department.created_at,
            updated_at=department.updated_at
        )
    
    async def update_department(self, department_id: int, department: UpdateDepartment) -> DepartmentResponse:
        db_department = await self.db.get(Department, department_id)
        if not db_department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        update_data = department.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_department, field, value)
            
        await self.db.commit()
        await self.db.refresh(db_department)
        total_employees = await self._get_employee_count(department_id)
        return DepartmentResponse(
            id=db_department.id,
            name=db_department.name,
            description=db_department.description,
            total_employees=total_employees,
            created_at=db_department.created_at,
            updated_at=db_department.updated_at
        )
    
    async def delete_department(self, department_id: int) -> None:
        department = await self.db.get(Department, department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        await self.db.delete(department)
        await self.db.commit()
        return {"message": "Department deleted successfully"}