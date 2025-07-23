from .models import TaskComments
from .schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.worklog.auth.models import Users

class TaskCommentService:
    def __init__(self, db: AsyncSession):
        self.db = db    

    async def create_task_comment(self, task_id: int, user_id: int, comment: CreateTaskComment) -> TaskCommentResponse:
        try:
            new_comment = TaskComments(
                task_id=task_id,
                content=comment.content,
                user_id=user_id
            )
            self.db.add(new_comment)
            await self.db.commit()
            await self.db.refresh(new_comment)
            return TaskCommentResponse(
                id=new_comment.id,
                content=new_comment.content,
                user_id=new_comment.user_id,
                created_at=new_comment.created_at,
                updated_at=new_comment.updated_at
            )
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_task_comments(self, task_id: int) -> TaskCommentListResponse:
        try:
            comments_result = await self.db.execute(
                select(TaskComments).where(TaskComments.task_id == task_id)
            )
            comments_list = comments_result.scalars().all()
            
            # If there are no comments, return an empty list
            if not comments_list:
                return TaskCommentListResponse(
                    comments=[],
                    total=0
                )
                
            # Get user data for the first comment
            user_db = await self.db.execute(
                select(Users).where(Users.id == comments_list[0].user_id)
            )
            user_list = user_db.scalars().first()
            
            return TaskCommentListResponse(
                comments=[TaskCommentResponse(
                    id=comment.id,
                    content=comment.content,
                    user=UserData(
                        id=user_list.id,
                        first_name=user_list.first_name,
                        last_name=user_list.last_name,
                        middle_name=user_list.middle_name,
                        position=user_list.position
                    ),
                    created_at=comment.created_at,
                    updated_at=comment.updated_at
                ) for comment in comments_list],
                total=len(comments_list)
            )
        except Exception as e:
            await self.db.rollback()
            raise e
    
