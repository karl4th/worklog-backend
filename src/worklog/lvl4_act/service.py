from .schemas import *
from .models import *
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from src.worklog.auth.models import Users
from src.worklog.tasks.models import Tasks, TaskAssignees
from src.worklog.db.core import get_db
from src.worklog.ai.whatsapp_handler import WhatsappHandler

class ActService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.whatsapp_handler = WhatsappHandler()

    async def create_act(self, act: ActCreate) -> ActResp:
        try:
            new_act = Act(
                title=act.title,
                mine=act.mine,
                description=act.description,
                requirement=act.requirement,
                at=act.at
            )
            self.db.add(new_act)
            await self.db.commit()
            await self.db.refresh(new_act)
            return ActResp(
                id=new_act.id,
                title=new_act.title,
                mine=new_act.mine,
                description=new_act.description,
                requirement=new_act.requirement,
                at=new_act.at
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_act(self, act_id: int, act: ActUpdate) -> ActResp:
        try:
            act_query = await self.db.execute(select(Act).where(Act.id == act_id))
            act_db = act_query.scalar_one_or_none()
            if not act_db:
                raise HTTPException(status_code=404, detail="Act not found")
            
            for field, value in act.model_dump().items():
                setattr(act_db, field, value)

            await self.db.commit()
            await self.db.refresh(act_db)
            return ActResp( 
                id=act_db.id,
                title=act_db.title,
                mine=act_db.mine,
                at=act_db.at,
                description=act_db.description,
                requirement=act_db.requirement
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
                
    async def delete_act(self, act_id: int) -> dict:
        try:
            act_query = await self.db.execute(select(Act).where(Act.id == act_id))
            act_db = act_query.scalars().first()
            if not act_db:
                raise HTTPException(status_code=404, detail="Act not found")
            
            await self.db.delete(act_db)
            await self.db.commit()
            return {"message": "Act deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all_acts(self) -> ActListResp:
        try:
            acts = await self.db.execute(select(Act))
            acts_list = acts.scalars().all()
            total = len(acts_list)
            return ActListResp(
                acts=[ActResp(
                    id=act.id,
                    title=act.title,
                    mine=act.mine.value,
                    description=act.description,
                    requirement=act.requirement,
                    at=act.at
                ) for act in acts_list],
                total=total
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_act_by_id(self, act_id: int) -> ActDetails:
        try:
            act_query = await self.db.execute(select(Act).where(Act.id == act_id))
            act_db = act_query.scalar_one_or_none()
            if not act_db:
                raise HTTPException(status_code=404, detail="Act not found")
            
            whom_query = await self.db.execute(select(ActWhom).where(ActWhom.act_id == act_id)) 
            whom_db = whom_query.scalars().all()

            from_whom_query = await self.db.execute(select(ActFrom).where(ActFrom.act_id == act_id))
            from_whom_db = from_whom_query.scalars().all()

            items_query = await self.db.execute(select(ActItems).where(ActItems.act_id == act_id))
            items_db = items_query.scalars().all()

            # Get user information for whom and from_whom
            whom_users = []
            from_whom_users = []
            
            for whom in whom_db:
                user_query = await self.db.execute(select(Users).where(Users.id == whom.user_id))
                user = user_query.scalar_one_or_none()
                if user:
                    whom_users.append(ActUsers(
                        id=user.id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        middle_name=user.middle_name,
                        position=user.position
                    ))

            for from_whom in from_whom_db:
                user_query = await self.db.execute(select(Users).where(Users.id == from_whom.user_id))
                user = user_query.scalar_one_or_none()
                if user:
                    from_whom_users.append(ActUsers(
                        id=user.id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        middle_name=user.middle_name,
                        position=user.position
                    ))

            # Получаем информацию о пользователях для элементов акта
            items_with_users = []
            for item in items_db:
                responsible_user = None
                if item.responsible_user:
                    user_query = await self.db.execute(select(Users).where(Users.id == item.responsible_user))
                    user = user_query.scalar_one_or_none()
                    if user:
                        responsible_user = ActUsers(
                            id=user.id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            middle_name=user.middle_name,
                            position=user.position
                        )
                
                # Создаем словарь с данными элемента акта
                item_dict = {
                    "id": item.id,
                    "content": item.content,
                    "requirement": item.requirement,
                    "note": item.note,
                    "responsible_user": responsible_user.model_dump() if responsible_user else None,
                    "deadline": item.deadline,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at
                }
                items_with_users.append(item_dict)

            return ActDetails(
                id=act_db.id,
                title=act_db.title,
                mine=act_db.mine.value,
                description=act_db.description,
                requirement=act_db.requirement,
                at=act_db.at,
                whom=whom_users,
                from_whom=from_whom_users,
                items=items_with_users,
                created_at=act_db.created_at,
                updated_at=act_db.updated_at
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_act_whom(self, whom: ActWhomCreate) -> dict:
        try:
            act_query = await self.db.execute(select(ActWhom).where(ActWhom.act_id== whom.act_id, ActWhom.user_id== whom.user_id))
            act_db = act_query.scalar_one_or_none()
            if act_db:
                raise HTTPException(status_code=400, detail="ActWhom already exists")
            
            new_whom = ActWhom(
                act_id=whom.act_id,
                user_id=whom.user_id
            )
            self.db.add(new_whom)
            await self.db.commit()
            await self.db.refresh(new_whom)
            return {"message": "ActWhom created successfully", "id": new_whom.id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_act_from(self, from_whom: ActFromCreate) -> dict:
        try:
            act_query = await self.db.execute(select(ActFrom).where(ActFrom.act_id== from_whom.act_id, ActFrom.user_id== from_whom.user_id))
            act_db = act_query.scalar_one_or_none()
            if act_db:
                raise HTTPException(status_code=400, detail="ActFrom already exists")
            
            new_from = ActFrom(
                act_id=from_whom.act_id,
                user_id=from_whom.user_id
            )
            self.db.add(new_from)
            await self.db.commit()
            await self.db.refresh(new_from)
            return {"message": "ActFrom created successfully", "id": new_from.id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_act_whom(self, act_id: int, user_id: int) -> dict:
        try:
            whom_query = await self.db.execute(select(ActWhom).where(ActWhom.user_id == user_id, ActWhom.act_id == act_id))
            whom_db = whom_query.scalars().first()
            if not whom_db:
                raise HTTPException(status_code=404, detail="ActWhom not found")

            await self.db.delete(whom_db)
            await self.db.commit()
            return {"message": "ActWhom deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def delete_act_from(self, act_id: int, user_id: int) -> dict:
        try:
            from_query = await self.db.execute(select(ActFrom).where(ActFrom.user_id == user_id, ActFrom.act_id == act_id))
            from_db = from_query.scalars().first()
            if not from_db:
                raise HTTPException(status_code=404, detail="ActFrom not found")

            await self.db.delete(from_db)
            await self.db.commit()
            return {"message": "ActFrom deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_act_item(self, item: ActItemsCreate) -> dict:
        try:
            # Step 1: Create the new act item
            new_item = ActItems(
                act_id=item.act_id,
                content=item.content,
                requirement=item.requirement,
                note=item.note,
                responsible_user=item.responsible_user,
                deadline=item.deadline
            )
            self.db.add(new_item)
            await self.db.flush()
            
            # Store the ID before commit to avoid lazy loading issues
            item_id = new_item.id
            
            # Step 2: Create a new task
            new_task = Tasks(
                title=item.content,
                description=item.requirement,
                status="new",
                priority="high",
                due_date=item.deadline
            )
            self.db.add(new_task)
            await self.db.flush()
            
            # Store the task ID before commit
            task_id = new_task.id
            task_title = new_task.title
            
            # Step 3: Create task assignee
            task_assignee = TaskAssignees(
                task_id=task_id,
                user_id=item.responsible_user
            )
            self.db.add(task_assignee)
            await self.db.flush()
            user = await self.db.get(Users, item.responsible_user)
            await self.whatsapp_handler.send_message(f"Вы были назначены на задачу {task_title}", user.chat_id_whatsapp)
            # Step 4: Create the relation
            new_relation = ActAndTaskRelation(
                act_item_id=item_id,
                task_id=task_id
            )
            self.db.add(new_relation)
            
            # Step 5: Commit all changes
            await self.db.commit()
            
            
            # Step 6: Return success response using the stored ID
            return {
                "message": "ActItem created successfully", 
                "id": item_id
            }
        except Exception as e:
            # Rollback in case of error
            await self.db.rollback()
            # Log the error details
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in create_act_item: {str(e)}")
            print(f"Error details: {error_details}")
            # Raise a more detailed HTTP exception
            raise HTTPException(
                status_code=500, 
                detail=f"Error creating act item: {str(e)}"
            )

    async def delete_act_item(self, item_id: int) -> dict:
        try:
            item_query = await self.db.execute(select(ActItems).where(ActItems.id == item_id))
            item_db = item_query.scalar_one_or_none()
            if not item_db:
                raise HTTPException(status_code=404, detail="ActItem not found")
            
            await self.db.delete(item_db)
            await self.db.commit()
            return {"message": "ActItem deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_act_item(self, item_id: int, item: ActItemsCreate) -> dict:
        try:
            item_query = await self.db.execute(select(ActItems).where(ActItems.id == item_id))
            item_db = item_query.scalar_one_or_none()
            if not item_db:
                raise HTTPException(status_code=404, detail="ActItem not found")
            
            for field, value in item.model_dump().items():
                setattr(item_db, field, value)

            await self.db.commit()
            await self.db.refresh(item_db)
            return {"message": "ActItem updated successfully", "id": item_db.id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_act_report(self, act_id: int) -> ActReportList:
        try:
            # Get all act items for the given act_id
            act_query = await self.db.execute(select(ActItems).where(ActItems.act_id == act_id))
            act_db = act_query.scalars().all()
            if not act_db:
                raise HTTPException(status_code=404, detail="Act not found")

            # Create a list to store the report items with task status
            report_items = []
            
            # For each act item, get the related task status
            for item in act_db:
                # Get the task relation
                relation_query = await self.db.execute(
                    select(ActAndTaskRelation).where(ActAndTaskRelation.act_item_id == item.id)
                )
                relation = relation_query.scalar_one_or_none()
                
                # Default status if no task is found
                task_status = "unknown"
                
                # If relation exists, get the task status
                if relation:
                    task_query = await self.db.execute(
                        select(Tasks).where(Tasks.id == relation.task_id)
                    )
                    task = task_query.scalar_one_or_none()
                    if task:
                        task_status = task.status
                
                # Get responsible user information
                responsible_user = None
                if item.responsible_user:
                    user_query = await self.db.execute(select(Users).where(Users.id == item.responsible_user))
                    user = user_query.scalar_one_or_none()
                    if user:
                        responsible_user = ActUsers(
                            id=user.id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            middle_name=user.middle_name,
                            position=user.position
                        )
                
                # Create the report item with the task status using the Pydantic schema
                from .schemas import ActReport
                report_item = ActReport(
                    id=item.id,
                    content=item.content,
                    requirement=item.requirement,
                    note=item.note,
                    responsible_user=responsible_user,
                    deadline=item.deadline,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                    status=task_status
                )
                report_items.append(report_item)

            return ActReportList(
                items=report_items,
                total=len(report_items)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
