from .schemas import *
from src.worklog.auth.models import Users
from src.worklog.departments.models import Department
from src.worklog.shifts.models import Shift
from src.worklog.rules.models import Roles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self, skip: int = 0, limit: int = 100) -> UserList:
        users = await self.db.execute(select(Users).order_by(Users.id).offset(skip).limit(limit))
        users = users.scalars().all()
        return UserList(
            users=[
                BaseUser(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    middle_name=user.middle_name,
                    position=user.position
                ) for user in users
            ], 
            total_users=len(users))

    async def get_user_profiles(self) -> UserServiceBase:
        """Получение профилей всех пользователей"""
        users = await self.db.execute(
            select(Users).order_by(Users.id)
        )
        users = users.scalars().all()
        
        if not users:
            return UserServiceBase(users=[], total_users=0)
        
        result_users = []
        for user in users:
            # Получаем данные отдела и смены
            department = None
            shift = None
            role = None
            
            if user.department_id:
                department = await self.db.execute(
                    select(Department).where(Department.id == user.department_id)
                )
                department = department.scalar_one_or_none()
            
            if user.shift_id:
                shift = await self.db.execute(
                    select(Shift).where(Shift.id == user.shift_id)
                )
                shift = shift.scalar_one_or_none()
            
            if user.role:
                role = await self.db.execute(
                    select(Roles).where(Roles.id == user.role)
                )
                role = role.scalar_one_or_none()
            
            result_users.append(
                UserRead(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    middle_name=user.middle_name,
                    phone=user.phone,
                    position=user.position,
                    department=DepartmentUser(id=department.id, display_name=department.name) if department else None,
                    shift=ShiftUser(id=shift.id, display_name=shift.name) if shift else None,
                    role=RoleUser(id=role.id, name=role.name) if role else None,
                    is_superuser=user.is_superuser
                )
            )
        
        return UserServiceBase(
            users=result_users,
            total_users=len(result_users)
        )
    