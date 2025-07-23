from .schemas import *
from .models import *
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, delete

class RuleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    ########################################################
    # ROLES
    ########################################################

    async def create_role(self, role_data: CreateRole) -> RoleResponse:
        try:
            role = Roles(
                name=role_data.name,
                description=role_data.description
            )
            self.db.add(role)
            await self.db.commit()
            await self.db.refresh(role)
            return RoleResponse.model_validate(role, from_attributes=True)
        except SQLAlchemyError as e:
            await self.db.rollback()
            if "unique constraint" in str(e).lower():
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "error",
                        "code": "role_name_exists",
                        "message": "Роль с таким именем уже существует"
                    }
                )
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "code": "database_error",
                    "message": "Ошибка при создании роли"
                }
            )

    async def update_role(self, role_id: int, role_data: UpdateRole) -> RoleResponse:
        try:
            query = select(Roles).where(Roles.id == role_id)
            result = await self.db.execute(query)
            role = result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "status": "error",
                        "code": "role_not_found",
                        "message": "Роль не найдена"
                    }
                )

            role.name = role_data.name
            role.description = role_data.description
            
            await self.db.commit()
            await self.db.refresh(role)
            return RoleResponse.model_validate(role, from_attributes=True)
        except SQLAlchemyError as e:
            await self.db.rollback()
            if "unique constraint" in str(e).lower():
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "error",
                        "code": "role_name_exists",
                        "message": "Роль с таким именем уже существует"
                    }
                )
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "code": "database_error",
                    "message": "Ошибка при обновлении роли"
                }
            )

    async def delete_role(self, role_id: int) -> bool:
        try:
            query = select(Roles).where(Roles.id == role_id)
            result = await self.db.execute(query)
            role = result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "status": "error",
                        "code": "role_not_found",
                        "message": "Роль не найдена"
                    }
                )

            await self.db.delete(role)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "code": "database_error",
                    "message": "Ошибка при удалении роли"
                }
            )

    async def get_role(self, role_id: int) -> RoleResponse:
        try:
            query = select(Roles).where(Roles.id == role_id)
            result = await self.db.execute(query)
            role = result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "status": "error",
                        "code": "role_not_found",
                        "message": "Роль не найдена"
                    }
                )
            
            return RoleResponse.model_validate(role, from_attributes=True)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "code": "database_error",
                    "message": "Ошибка при получении роли"
                }
            )

    async def get_roles(self) -> RoleList:
        try:
            query = select(Roles)
            result = await self.db.execute(query)
            roles = result.scalars().all()
            total = len(roles)
            return RoleList(roles=[RoleResponse.model_validate(role, from_attributes=True) for role in roles], total=total)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "code": "database_error",
                    "message": "Ошибка при получении списка ролей"
                }
            )

    async def get_role_permissions(self) -> RolePermissionList:
        try:
            query = select(RolePermissions)
            result = await self.db.execute(query)
            role_permissions = result.scalars().all()
            
            # Преобразуем объекты в словари для валидации
            role_permission_dicts = [
                {"role_id": rp.role_id, "permission_id": rp.permission_id}
                for rp in role_permissions
            ]
            
            return RolePermissionList(
                data=[RolePermissionResponse.model_validate(rp) for rp in role_permission_dicts]
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "code": "database_error",
                    "message": "Ошибка при получении списка разрешений для ролей"
                }
            )
    ########################################################
    # PERMISSIONS
    ########################################################

    async def create_permission(self, permission_data: CreatePermission) -> PermissionResponse:
        try:
            permission = Permissions(
                name=permission_data.name,
                page=permission_data.page,
                display_name=permission_data.display_name
            )
            self.db.add(permission)
            await self.db.commit()
            await self.db.refresh(permission)
            return PermissionResponse.model_validate(permission)
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",  
                    "code": "database_error",
                    "message": "Ошибка при создании разрешения"
                }
            )
        except HTTPException as e:
            raise e

    async def get_permissions(self) -> PermissionList:
        try:
            result = await self.db.execute(select(Permissions))
            permissions = result.scalars().all()
            total = len(permissions)

            return PermissionList(
                permissions=[
                    PermissionResponse(
                        id=permission.id,
                        name=permission.display_name,
                        display_name=permission.display_name,
                        page=permission.page,
                        created_at=permission.created_at,
                        updated_at=permission.updated_at
                    ) for permission in permissions
                ],
                total=total
            )

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "code": "database_error",
                    "message": f"Ошибка при получении списка разрешений: {str(e)}"
                }
            )
        except HTTPException as e:
            raise e


    async def create_permissions(self, permissions_data: list[CreatePermission]) -> PermissionList:
        try:
            permissions = []
            for permission_data in permissions_data:
                permission = Permissions(
                    name=permission_data.name,
                    display_name=permission_data.display_name,
                    page=permission_data.page
                )
                permissions.append(permission)
                self.db.add(permission)
            
            await self.db.commit()
            for permission in permissions:
                await self.db.refresh(permission)
            
            return PermissionList(permissions=[PermissionResponse(
                id=permission.id,
                name=permission.name,
                display_name=permission.display_name,
                page=permission.page,
                created_at=permission.created_at,
                updated_at=permission.updated_at
            ) for permission in permissions])
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",  
                    "code": "database_error",
                    "message": "Ошибка при создании разрешений"
                }
            )
        except HTTPException as e:
            raise e

    async def save_role_permissions(self, permissions_data: dict[str, list[int]]) -> bool:
        try:
            # Удаляем все существующие права
            await self.db.execute(delete(RolePermissions))
            
            # Добавляем новые права
            for role_id, permission_ids in permissions_data.items():
                for permission_id in permission_ids:
                    role_permission = RolePermissions(
                        role_id=int(role_id),
                        permission_id=permission_id,
                        access=True,
                    )
                    self.db.add(role_permission)
            
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "code": "database_error",
                    "message": "Ошибка при сохранении прав ролей"
                }
            )
