from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from .models import *
from .schemas import *
from .utils import hash_password, verify_password
from sqlalchemy.exc import IntegrityError
from src.worklog.departments.models import Department
from src.worklog.shifts.models import Shift
from src.worklog.rules.models import Roles


def trim(phone: str) -> str:
    return phone.strip().replace(" ", "")


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserCreate) -> UserRead:
        # Проверяем существование пользователя
        exist_user = await self.db.execute(select(Users).where(Users.phone == user.phone))
        if exist_user.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "code": "user_already_exists",
                    "message": "Пользователь с таким номером телефона уже существует"
                }
            )

        # Проверяем существование отдела
        if user.department_id:
            department = await self.db.execute(select(Department).where(Department.id == user.department_id))
            if not department.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "error",
                        "code": "department_not_found",
                        "message": "Указанный отдел не существует"
                    }
                )

        # Проверяем существование смены
        if user.shift_id:
            shift = await self.db.execute(select(Shift).where(Shift.id == user.shift_id))
            if not shift.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "error",
                        "code": "shift_not_found",
                        "message": "Указанная смена не существует"
                    }
                )
        
        try:
            new_user = Users(
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                phone=trim(user.phone),
                password=hash_password(user.password),
                position=user.position,
                department_id=user.department_id or 0,
                shift_id=user.shift_id or 0,
                role=user.role
            )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

            # Получаем данные отдела и смены
            department = None
            shift = None
            role = None


            if user.department_id:
                department = await self.db.execute(
                    select(Department).where(Department.id == new_user.department_id)
                )
                department = department.scalar_one_or_none()
            
            if user.shift_id:
                shift = await self.db.execute(
                    select(Shift).where(Shift.id == new_user.shift_id)
                )
                shift = shift.scalar_one_or_none()
            
            if user.role:
                role = await self.db.execute(
                    select(Roles).where(Roles.id == new_user.role)
                )
                role = role.scalar_one_or_none()
            
            return UserRead(
                id=new_user.id,
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                middle_name=new_user.middle_name,
                phone=new_user.phone,
                position=new_user.position,
                department=DepartmentUser(id=department.id, display_name=department.name) if department else None,
                shift=ShiftUser(id=shift.id, display_name=shift.name) if shift else None,
                role=RoleUser(id=role.id, name=role.name) if role else None,
                is_superuser=new_user.is_superuser
            )
        
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "code": "database_error",
                    "message": f"Ошибка при сохранении пользователя: {e}"
                }
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "code": "internal_error",
                    "message": f"Внутренняя ошибка сервера: e"
                }
            )

    async def authenticate_user(self, phone: str, password: str) -> UserRead:
        """Аутентификация пользователя и возврат его данных"""
        user = await self.db.execute(
            select(Users).where(Users.phone == trim(phone))
        )
        user = user.scalar_one_or_none()
        
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=401,
                detail={
                    "status": "error",
                    "code": "invalid_credentials",
                    "message": "Неверный номер телефона или пароль"
                }
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=401,
                detail={
                    "status": "error",
                    "code": "user_inactive",
                    "message": "Пользователь неактивен"
                }
            )
        
        if user.is_banned:
            raise HTTPException(
                status_code=401,
                detail={
                    "status": "error",
                    "code": "user_banned",
                    "message": "Пользователь заблокирован"
                }
            )
        
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
        
        return UserRead(
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

    async def get_user_profile(self, user_id: int) -> UserRead:
        """Получение профиля пользователя по ID"""
        user = await self.db.execute(
            select(Users).where(Users.id == user_id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "code": "user_not_found",
                    "message": "Пользователь не найден"
                }
            )
        
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
        
        return UserRead(
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
    