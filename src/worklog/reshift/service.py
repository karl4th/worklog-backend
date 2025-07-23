from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.reshift.models import *
from src.worklog.reshift.schemas import *
from src.worklog.auth.models import Users
from sqlalchemy import or_, and_
from src.worklog.tasks.models import TaskAssignees


class ReShiftService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report_reshift(self, data: ReshiftCreate):
        try:
            new_report = Reshifts(
                user_id=data.user_id,
                done=data.done,
                todo=data.todo
            )
            self.db.add(new_report)
            await self.db.commit()
            await self.db.refresh(new_report)
            await self.sign_user_shift_task(data.user_id)
            return new_report
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_user_shifts(self, data: CreateUserShifts):
        try:
            # Проверяем, есть ли уже такая пара пользователей в любом порядке
            query = select(ReshiftUsers).where(
                or_(
                    and_(
                        ReshiftUsers.first_user_id == data.first_user_id,
                        ReshiftUsers.second_user_id == data.second_user_id,
                    ),
                    and_(
                        ReshiftUsers.first_user_id == data.second_user_id,
                        ReshiftUsers.second_user_id == data.first_user_id,
                    ),
                )
            )
            result = await self.db.execute(query)
            existing_shift = result.scalars().first()

            if existing_shift:
                raise HTTPException(status_code=409, detail="Users already exist")

            # Создаём новую смену
            new_shift = ReshiftUsers(
                first_user_id=data.first_user_id,
                second_user_id=data.second_user_id,
            )
            self.db.add(new_shift)
            await self.db.commit()
            await self.db.refresh(new_shift)
            return new_shift

        except Exception as e:
            # логирование или проброс ошибки при необходимости
            raise e

    async def get_user_shifts(self, user_id: int):
        try:
            query = select(ReshiftUsers).where(
                or_(
                    and_(
                        ReshiftUsers.first_user_id == user_id,
                    ),
                    and_(
                        ReshiftUsers.second_user_id == user_id,
                    ),
                )
            )
            result = await self.db.execute(query)
            existing_shift = result.scalars().first()
            if existing_shift is None:
                raise HTTPException(status_code=404, detail="User not found")

            return {
                "user_id": user_id,
                "first_user_id": existing_shift.first_user_id,
                "second_user_id": existing_shift.second_user_id,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_reports(self, user_id: int) -> ReportListResponse:
        # Получаем данные о пользователе
        user_db = await self.db.execute(select(Users).where(Users.id == user_id))
        user_main = user_db.scalars().first()

        if not user_main:
            raise HTTPException(status_code=404, detail="User not found")

        # Находим смену, где участвует пользователь
        shift_query = select(ReshiftUsers).where(
            or_(
                ReshiftUsers.first_user_id == user_id,
                ReshiftUsers.second_user_id == user_id,
            )
        )
        shift_result = await self.db.execute(shift_query)
        shift = shift_result.scalars().first()

        # Определяем второго пользователя, если он есть
        second_user_id = None
        if shift:
            second_user_id = (
                shift.second_user_id if shift.first_user_id == user_id else shift.first_user_id
            )

        # Собираем id пользователей, чьи отчёты нужно вернуть
        user_ids = [user_id]
        if second_user_id:
            user_ids.append(second_user_id)

        # Получаем пользователей для отчётов
        users_query = await self.db.execute(select(Users).where(Users.id.in_(user_ids)))
        users_map = {user.id: user for user in users_query.scalars().all()}

        # Получаем отчёты по обоим пользователям
        reports_query = await self.db.execute(
            select(Reshifts).where(Reshifts.user_id.in_(user_ids)).order_by(Reshifts.id.desc())
        )
        reports = reports_query.scalars().all()

        # Собираем результат
        return ReportListResponse(
            reports=[
                ReportResponse(
                    id=report.id,
                    done=report.done,
                    todo=report.todo,
                    user=User(
                        id=report.user_id,
                        first_name=users_map[report.user_id].first_name,
                        last_name=users_map[report.user_id].last_name,
                        middle_name=users_map[report.user_id].middle_name,
                        position=users_map[report.user_id].position,
                    ),
                    created_at=report.created_at,
                )
                for report in reports
            ],
            total=len(reports)
        )

    async def sign_user_shift_task(self, user_id: int):
        # Находим смену, где участвует пользователь
        query = select(ReshiftUsers).where(
            or_(
                ReshiftUsers.first_user_id == user_id,
                ReshiftUsers.second_user_id == user_id,
            )
        )
        result = await self.db.execute(query)
        existing_shift = result.scalars().first()

        if existing_shift is None:
            return False  # просто возвращаем False, если не найден shift

        # Определяем второго пользователя
        second_user_id = (
            existing_shift.second_user_id
            if existing_shift.first_user_id == user_id
            else existing_shift.first_user_id
        )

        # Получаем задачи текущего пользователя
        main_user_tasks = await self.db.execute(
            select(TaskAssignees).where(TaskAssignees.user_id == user_id)
        )
        tasks = main_user_tasks.scalars().all()

        # Получаем все уже назначенные задачи второго пользователя
        existing_assignees_result = await self.db.execute(
            select(TaskAssignees.task_id).where(TaskAssignees.user_id == second_user_id)
        )
        existing_task_ids = set(existing_assignees_result.scalars().all())

        # Добавляем только те, которых ещё нет
        for task in tasks:
            if task.task_id not in existing_task_ids:
                new_assignee = TaskAssignees(
                    user_id=second_user_id,
                    task_id=task.task_id,
                )
                self.db.add(new_assignee)

        await self.db.commit()
        return True
