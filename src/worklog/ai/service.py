import json

from src.worklog.ai.models import *
from src.worklog.ai.schemas import *
from src.worklog.ai.webhook_schema import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from fastapi import HTTPException
from src.worklog.auth.models import Users
from src.worklog.queue.service import RabbitMQPublisher

class AIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rabbitmq_publisher = RabbitMQPublisher()

    async def _create_user_connection(self, user_id: int, chat_id: str) -> dict:
        user = await self.db.execute(select(Users).where(Users.id == user_id))
        user = user.scalars().first()
        if user:
            user.chat_id_whatsapp = chat_id
            self.db.add(user)
            await self.db.commit()
            return {"message": "User connection created successfully"}
        else:
            return {"message": "User not found"}

    async def _get_user_connection(self, user_id: int):
        user = await self.db.execute(select(Users).where(Users.id == user_id))
        user = user.scalars().first()
        if user:
            return user.chat_id_whatsapp
        else:
            return {"message": "User connection not found"}

    async def _get_user_connection_by_chat_id(self, chat_id: str):
        user = await self.db.execute(select(Users).where(Users.chat_id_whatsapp == chat_id))
        user = user.scalars().first()
        if user:
            return user.id
        else:
            return {"message": "User connection not found", "chat_id": chat_id}
        

    async def _get_agent_id(self):
        agent = await self.db.query(AIAgent).filter(AIAgent.is_active == True).first()
        if agent:
            return agent.id
        else:
            return {"message": "Agent not found"}

    async def create_ai_agent(self, ai_agent: CreateAIAgent) -> dict:
        ai_agent = AIAgent(**ai_agent.model_dump())
        self.db.add(ai_agent)
        await self.db.commit()
        return {"message": "AI agent created successfully"}
    
    async def get_ai_agent(self, agent_id: int):
        # Get the agent
        agent = await self.db.execute(select(AIAgent).where(AIAgent.id == agent_id))
        result = agent.scalars().first()
        if not result:
            return {"message": "AI agent not found"}
            
        # Get associated tools
        tools_db = await self.db.execute(select(AgentToolsData).where(AgentToolsData.agent_id == agent_id))
        tools = tools_db.scalars().all()
        
        # Convert tools to Pydantic models
        tools_list = []
        for tool in tools:
            tools_list.append({
                "id": tool.id,
                "agent_id": tool.agent_id,
                "tool_name": tool.tool_name,
                "tool_description": tool.tool_description,
                "tool_properties": tool.tool_properties,
                "tool_required": tool.tool_required,
                "tool_type": tool.tool_type,
                "tool_method": tool.tool_method,
                "tool_url": tool.tool_url,
                "tool_headers": tool.tool_headers,
                "tool_body": tool.tool_body
            })
        
        # Format the response according to AgentResponse schema
        return {
            "id": result.id,
            "name": result.name,
            "description": result.description,
            "system_message": result.system_message,
            "model": result.model,
            "tools": tools_list if tools_list else None
        }

    async def update_ai_agent(self, agent_id: int, ai_agent: CreateAIAgent) -> dict:
        db_agent = await self.db.execute(select(AIAgent).where(AIAgent.id == agent_id))
        result = db_agent.scalars().first()
        if not result:
            return {"message": "AI agent not found"}
        
        update_data = ai_agent.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(result, field, value)

        self.db.add(result)
        await self.db.commit()
        return {"message": "AI agent updated successfully"}
    
    async def create_agent_tools(self, agent_id: int, agent_tools: CreateAgentTools) -> dict:
        # Create a new AgentTools instance using the SQLAlchemy model
        new_agent_tools = AgentToolsData(
            agent_id=agent_id,
            tool_name=agent_tools.tool_name,
            tool_description=agent_tools.tool_description,
            tool_properties=agent_tools.tool_properties,
            tool_required=agent_tools.tool_required,
            tool_type=agent_tools.tool_type,
            tool_method=agent_tools.tool_method,
            tool_url=agent_tools.tool_url,
            tool_headers=agent_tools.tool_headers,
            tool_body=agent_tools.tool_body if agent_tools.tool_body else None
        )
        self.db.add(new_agent_tools)
        await self.db.commit()
        return {"message": "Agent tools created successfully"}
    
    async def update_agent_tools(self, agent_id: int, agent_tools: CreateAgentTools) -> dict:
        db_agent_tools = await self.db.execute(select(AgentToolsData).where(AgentToolsData.agent_id == agent_id))
        result = db_agent_tools.scalars().first()
        if not result:
            return {"message": "Agent tools not found"}
        
        update_data = agent_tools.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(result, field, value)
            
        self.db.add(result)
        await self.db.commit()
        return {"message": "Agent tools updated successfully"}
    
    async def delete_agent_tools(self, agent_tools_id: int) -> dict:
        agent_tools = await self.db.execute(select(AgentToolsData).where(AgentToolsData.id == agent_tools_id))
        result = agent_tools.scalars().first()
        if not result:
            return {"message": "Agent tools not found"}
        await self.db.delete(result)
        await self.db.commit()
        return {"message": "Agent tools deleted successfully"}
    
    async def get_agent_tools(self, agent_id: int) -> dict:
        # Default tools that are always available
        tools = []
        
        # Get tools from database
        tools_db = await self.db.execute(select(AgentToolsData).where(AgentToolsData.agent_id == agent_id))
        result = tools_db.scalars().all()
        
        if not result:
            return {"tools": tools}
        
        # Add database tools to the list
        for tool in result:
            tools.append(
                {
                    "type": "custom",
                    "name": f"{tool.tool_name}",
                    "description": f"{tool.tool_type.value} tool with {tool.tool_method.value} method",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            **tool.tool_properties
                        },
                        "required": tool.tool_required
                    }
                }
            )
        
        return {"tools": tools}
        
    async def webhook(self, payload: WebhookPayload) -> dict:
        message_to_insert = []
        save = False
        for message in payload.messages:
            chat_id = await self._get_user_connection_by_chat_id(message.chat_id)
            content = ""
            if message.text:
                content = message.text.body
            elif message.document:
                content = message.document.caption or message.document.file_name
            elif message.voice:
                content = f"Voice message ({message.voice.seconds}s)"
            elif message.sticker:
                content = "Sticker"
            elif message.link_preview:
                content = message.link_preview.body
            elif message.action:
                content = f"Action: {message.action.type}"
            
            message_record = {
                "agent_id": 1,
                "user_id": chat_id,
                "content": content,
                "type_message": "text",
                "role": "assistant" if message.from_me else "user",
                "tool_use": False,
                "tool_name": None,
                "tool_id": None,
                "tool_input": None,
                "tool_output": None,
            }
            if message.from_me:
                save = False
            else:
                save = True
            message_to_insert.append(message_record)
            
        if message_to_insert:
            if save:
                await self.db.execute(
                    insert(AgentMessages),
                    message_to_insert
                )
                await self.db.commit()  

                self.rabbitmq_publisher.send({
                    "chat_id": chat_id,
                    "message": "new"
                })


        return {"message": "Webhook received successfully"}
    
    async def _set_agent(self, agent_id: int, user_id: int) -> dict:
        # Get user data 
        user_db = await self.db.execute(select(Users).where(Users.id == user_id))
        user = user_db.scalars().first()
        if not user:
            return {"error": "User not found"}
        
        # Get user chat ID
        
        user_data = f'USER ID: {user.id}, Имя: {user.first_name}, Фамилия: {user.last_name}, Телефон: {user.phone}, Должность: {user.position}, Сегодня: {datetime.today()}'
        
        # Get agent data
        agent_db = await self.db.execute(select(AIAgent).where(AIAgent.id == agent_id))
        agent = agent_db.scalars().first()
        if not agent:
            return {"error": "Agent not found"}
        
        # Get system message
        system_message = f'Ваш зовут: {agent.name} \n\n {agent.system_message} \n\n {user_data}'
        
        # Get messages
        messages = []
        messages_db = await self.db.execute(
            select(AgentMessages)
            .where(AgentMessages.user_id == user_id)
            .order_by(AgentMessages.created_at)
        )
        messages_result = messages_db.scalars().all()
        
        for msg in messages_result:
            message_content = []

            if msg.role == 'user':
                if msg.tool_use:
                    msg_new = {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": msg.tool_id,
                                "content": json.dumps(msg.tool_output, ensure_ascii=False)
                            }
                        ]
                    }
                else:
                    msg_new = {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": msg.content
                            }
                        ]
                    }
                messages.append(msg_new)

            if msg.role == 'assistant':
                if msg.tool_use:
                    msg_new = {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": msg.content,
                            },
                            {
                                "type": "tool_use",
                                "name": msg.tool_name,
                                "id": msg.tool_id,
                                "input": msg.tool_input
                            }
                        ]
                    }
                else:
                    msg_new = {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": msg.content
                            }
                        ]
                    }
                messages.append(msg_new)


        # Get tools
        tools = []
        tools_db = await self.db.execute(select(AgentToolsData).where(AgentToolsData.agent_id == agent_id))
        tools_result = tools_db.scalars().all()
        
        for tool in tools_result:
            tools.append(
                {
                    "type": "custom",
                    "name": f"{tool.tool_name}",
                    "description": f"{tool.tool_type.value} tool with {tool.tool_method.value} method",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            **tool.tool_properties
                        },
                        "required": tool.tool_required
                    }
                }
            )
        
        return {
            "system_message": system_message,
            "messages": messages,
            "tools": tools
        }