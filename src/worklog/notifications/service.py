from .models import Notifications
from .schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from typing import List
from src.worklog.auth.models import Users
from src.worklog.queue.service import RabbitMQPublisher
from src.worklog.ai.whatsapp_handler import WhatsappHandler

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rabbitmq_publisher = RabbitMQPublisher()
        self.whatsapp_handler = WhatsappHandler()
    
    async def create_notification(self, user_id: int, essence: str, task_id: int = None):
        notification = Notifications(
            user_id=user_id,
            essence=essence,
            task_id=task_id
        )
        self.send_notification(user_id, essence)
        self.db.add(notification)
        await self.db.commit()
        self.rabbitmq_publisher.send({
            "user_id": user_id,
            "message": notification.id
        })
        return notification

    async def send_notification(self, user_id: int, message: str):
        userDB = await self.db.execute(select(Users).where(Users.id == user_id))
        user = userDB.scalars().first()
        if user:
            await self.whatsapp_handler.send_message(user.chat_id_whatsapp, message)
        else:
            raise HTTPException(status_code=404, detail="User not found")
