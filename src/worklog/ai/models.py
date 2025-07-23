from src.worklog.db.core import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, func, Text, JSON, Enum as SQLAlchemyEnum
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    kazakh = 'kazakh'
    russian = 'russian'
    english = 'english'

class Model(str, Enum):
    claude_3_5_sonnet = 'claude_3_5_sonnet'
    claude_3_5_haiku = 'claude_3_5_haiku'

class ToolType(str, Enum):
    webhook = 'webhook'
    client = 'client'

class ToolMethod(str, Enum):
    get = 'get'
    post = 'post'
    put = 'put'
    delete = 'delete'

class AgentStatus(str, Enum):
    answer = 'answer'
    completed = 'completed'
    cancelled = 'cancelled'
    error = 'error'



class AIAgent(Base):
    __tablename__ = 'ai_agents'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    system_message: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Language] = mapped_column(SQLAlchemyEnum(Language), nullable=False)
    additional_instructions: Mapped[str] = mapped_column(Text, nullable=True)
    model: Mapped[Model] = mapped_column(SQLAlchemyEnum(Model), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class AgentToolsData(Base):
    __tablename__ = 'agent_tools_data'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False)
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tool_description: Mapped[str] = mapped_column(Text, nullable=False)
    tool_properties: Mapped[dict] = mapped_column(JSON, nullable=False)
    tool_required: Mapped[list] = mapped_column(JSON, nullable=False)

    tool_type: Mapped[ToolType] = mapped_column(SQLAlchemyEnum(ToolType), nullable=False)
    tool_method: Mapped[ToolMethod] = mapped_column(SQLAlchemyEnum(ToolMethod), nullable=False)
    tool_url: Mapped[str] = mapped_column(String(255), nullable=False)
    tool_headers: Mapped[dict] = mapped_column(JSON, nullable=True)
    tool_body: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class AgentMessages(Base):
    __tablename__ = 'agent_messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    agent_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False) # Сообщение
    type_message: Mapped[str] = mapped_column(String(255), nullable=False, default='text') # Тип сообщения text or 
    role: Mapped[str] = mapped_column(String(255), nullable=False, default='user') # Роль

    tool_use: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False) # Использование инструмента
    tool_name: Mapped[str] = mapped_column(String(255), nullable=True) # Название инструмента
    tool_id: Mapped[str] = mapped_column(String(255), nullable=True) # ID инструмента
    tool_input: Mapped[dict] = mapped_column(JSON, nullable=True) # Входные данные инструмента
    tool_output: Mapped[dict] = mapped_column(JSON, nullable=True) # Выходные данные инструмента

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
