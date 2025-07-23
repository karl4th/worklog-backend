from .models import *
from sqlalchemy import select, and_, or_
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.auth.models import Users
from functools import lru_cache
from typing import Optional

class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._permission_cache = {}

    @lru_cache(maxsize=100)
    def _get_permission_id(self, permission: str) -> Optional[int]:
        return self._permission_cache.get(permission)

    async def user_access_control(self, user_id: int, permission: str) -> bool:
        try:
            # Convert user_id to integer if it's a string
            user_id = int(user_id)
            
            # Get user with a single query
            query = await self.db.execute(
                select(Users).where(Users.id == user_id)
            )
            user = query.scalar_one_or_none()
            
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
                
            if user.is_superuser:
                return True
            
            
            # Get permission ID from cache or database
            permission_id = self._get_permission_id(permission)
            if permission_id is None:
                permission_query = await self.db.execute(
                    select(Permissions).where(Permissions.name == permission)
                )
                permission_obj = permission_query.scalar_one_or_none()
                if permission_obj is None:
                    return False
                permission_id = permission_obj.id
                self._permission_cache[permission] = permission_id

            # Check all permissions in a single query
            roles_db = await self.db.execute(select(RolePermissions).where(RolePermissions.permission_id == permission_id, RolePermissions.role_id == user.role))
            roles = roles_db.scalars().all()
            if roles:
                return True
            
            departments_db = await self.db.execute(select(DepartmentPermissions).where(DepartmentPermissions.permission_id == permission_id, DepartmentPermissions.department_id == user.department_id))
            departments = departments_db.scalars().all()
            if departments:
                return True
            
            user_permissions_db = await self.db.execute(select(UserPermissions).where(UserPermissions.permission_id == permission_id, UserPermissions.user_id == user_id))
            user_permissions = user_permissions_db.scalars().all()
            if user_permissions:
                return True
            
     
            return False

        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
