from .models import *
from .schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime
from fastapi import HTTPException
from src.worklog.tasks.models import Tasks
from src.worklog.auth.models import Users

class TaskChecklistService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_checklist(self, checklist: CreateCheckList, user_id: int, task_id: int) -> CheckListWithItemsResponse:
        try: 
            # Check if task exists
            task = await self.db.execute(
                select(Tasks).where(Tasks.id == task_id)
            )
            if not task.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Task not found")

            new_checklist = TaskChecklist(
                task_id=task_id,
                title=checklist.title,
                description=checklist.description,
                created_by=user_id
            )
            self.db.add(new_checklist)
            await self.db.commit()
            await self.db.refresh(new_checklist)

            return CheckListWithItemsResponse(
                id=new_checklist.id,
                task_id=new_checklist.task_id,
                title=new_checklist.title,
                description=new_checklist.description,
                checklist_items=[]
            )
        except Exception as e:
            await self.db.rollback()
            raise e

    async def update_checklist_data(self, checklist_id: int, data: UpdateCheckList) -> bool:
        query = select(TaskChecklist).where(TaskChecklist.id == checklist_id)
        result = await self.db.execute(query)
        checklist = result.scalars().first()

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(checklist, field, value)

        await self.db.commit()
        await self.db.refresh(checklist)


    async def get_task_checklists(self, task_id: int) -> TaskChecklistListResponse:
        try:
            checklists = await self.db.execute(
                select(TaskChecklist).where(TaskChecklist.task_id == task_id)
            )
            checklists = checklists.scalars().all()
            
            result = []
            for checklist in checklists:
                # Get checklist items with user data
                checklist_items_query = select(
                    TaskChecklistItem,
                    Users
                ).outerjoin(
                    Users,
                    TaskChecklistItem.completed_by == Users.id
                ).where(
                    TaskChecklistItem.checklist_id == checklist.id
                )
                
                checklist_items_result = await self.db.execute(checklist_items_query)
                checklist_items = checklist_items_result.all()
                
                result.append(CheckListWithItemsResponse(
                    id=checklist.id,
                    task_id=checklist.task_id,
                    title=checklist.title,
                    description=checklist.description,
                    checklist_items=[CheckListItemResponse(
                        id=item.TaskChecklistItem.id,
                        checklist_id=item.TaskChecklistItem.checklist_id,
                        content=item.TaskChecklistItem.content,
                        is_checked=item.TaskChecklistItem.is_checked,
                        completed_by=UserData(
                            id=item.Users.id,
                            first_name=item.Users.first_name,
                            last_name=item.Users.last_name,
                            middle_name=item.Users.middle_name,
                            position=item.Users.position
                        ) if item.Users else None,
                        created_at=item.TaskChecklistItem.created_at,
                        updated_at=item.TaskChecklistItem.updated_at
                    ) for item in checklist_items]
                ))
            
            return TaskChecklistListResponse(checklists=result)
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_checklist_by_id(self, checklist_id: int) -> CheckListWithItemsResponse:
        try:
            checklist = await self.db.execute(
                select(TaskChecklist).where(TaskChecklist.id == checklist_id)
            )
            checklist = checklist.scalar_one_or_none()

            if not checklist:   
                raise HTTPException(status_code=404, detail="Checklist not found")  

            # Get checklist items with user data
            checklist_items_query = select(
                TaskChecklistItem,
                Users
            ).outerjoin(
                Users,
                TaskChecklistItem.completed_by == Users.id
            ).where(
                TaskChecklistItem.checklist_id == checklist_id
            )
            
            checklist_items_result = await self.db.execute(checklist_items_query)
            checklist_items = checklist_items_result.all()

            return CheckListWithItemsResponse(
                id=checklist.id,
                task_id=checklist.task_id,
                title=checklist.title,
                description=checklist.description,
                checklist_items=[CheckListItemResponse(
                    id=item.TaskChecklistItem.id,
                    checklist_id=item.TaskChecklistItem.checklist_id,
                    content=item.TaskChecklistItem.content,
                    is_checked=item.TaskChecklistItem.is_checked,
                    completed_by=UserData(
                        id=item.Users.id,
                        first_name=item.Users.first_name,
                        last_name=item.Users.last_name,
                        middle_name=item.Users.middle_name,
                        position=item.Users.position
                    ) if item.Users else None,
                    created_at=item.TaskChecklistItem.created_at,
                    updated_at=item.TaskChecklistItem.updated_at
                ) for item in checklist_items]
            )
        except Exception as e:
            await self.db.rollback()
            raise e

    async def create_checklist_item(self, checklist_id: int, item: CreateCheckListItem) -> CheckListItemResponse:
        try:
            # Check if checklist exists
            checklist = await self.db.execute(
                select(TaskChecklist).where(TaskChecklist.id == checklist_id)
            )
            if not checklist.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Checklist not found")

            new_item = TaskChecklistItem(
                checklist_id=checklist_id,
                content=item.content,
            )
            self.db.add(new_item)
            await self.db.commit()
            await self.db.refresh(new_item)

            return CheckListItemResponse(
                id=new_item.id,
                checklist_id=new_item.checklist_id,
                content=new_item.content,
                is_checked=new_item.is_checked,
                completed_by=new_item.completed_by,
                created_at=new_item.created_at,
                updated_at=new_item.updated_at
            )
        except Exception as e:
            await self.db.rollback()
            raise e

    async def update_checklist_item(self, user_id: int, checklist_id: int, item_id: int, is_checked: bool) -> CheckListItemResponse:
        try:
            # Check if checklist exists
            checklist = await self.db.execute(
                select(TaskChecklist).where(TaskChecklist.id == checklist_id)
            )
            if not checklist.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Checklist not found")

            # Check if item exists and belongs to the checklist
            item = await self.db.execute(
                select(TaskChecklistItem).where(
                    TaskChecklistItem.id == item_id,
                    TaskChecklistItem.checklist_id == checklist_id
                )
            )
            item = item.scalar_one_or_none()

            if not item:
                raise HTTPException(status_code=404, detail="Checklist item not found")

            item.is_checked = is_checked
            item.completed_by = user_id if is_checked else None
            item.completed_at = datetime.now() if is_checked else None

            await self.db.commit()
            await self.db.refresh(item)

            return CheckListItemResponse(
                id=item.id,
                checklist_id=item.checklist_id,
                content=item.content,
                is_checked=item.is_checked,
                completed_by=None,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:  
            await self.db.rollback()
            raise e

    async def delete_checklist_item(self, checklist_item_id: int) -> bool:
        try:
            checklist = await self.db.execute(select(TaskChecklistItem).where(TaskChecklistItem.id == checklist_item_id))
            result = checklist.scalars().first()

            if not result:
                raise HTTPException(status_code=404, detail="Checklist item not found")

            await self.db.delete(result)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=404, detail=f"{str(e)}")