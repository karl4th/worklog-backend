from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Integer, Boolean, Enum as SQLAlchemyEnum
from datetime import datetime
from src.worklog.db.core import Base
from enum import Enum

class Mine(Enum):
    ortalyk = 'ortalyk'
    zhalpak = 'zhalpak'


class Act(Base):
    __tablename__ = 'act_4'
 
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    mine: Mapped[Mine] = mapped_column(SQLAlchemyEnum(Mine), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    requirement: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
 
class ActWhom(Base):
    __tablename__ = 'act_whom_4'

    id: Mapped[int] = mapped_column(primary_key=True)
    act_id: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class ActFrom(Base):
    __tablename__ = 'act_from_4'

    id: Mapped[int] = mapped_column(primary_key=True)
    act_id: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class ActItems(Base):
    __tablename__ = 'act_items_4'

    id: Mapped[int] = mapped_column(primary_key=True)
    act_id: Mapped[int] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    requirement: Mapped[str] = mapped_column(String(500), nullable=False)
    note: Mapped[str] = mapped_column(String(500), nullable=True)
    responsible_user: Mapped[int] = mapped_column(Integer, nullable=True)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ActReport(Base):
    __tablename__ = 'act_report_4'
    id: Mapped[int] = mapped_column(primary_key=True)
    act_id: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    act_item_id: Mapped[int] = mapped_column(Integer, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class ActAndTaskRelation(Base):
    __tablename__ = 'act_and_task_relation_4'
    id: Mapped[int] = mapped_column(primary_key=True)
    act_item_id: Mapped[int] = mapped_column(Integer, nullable=True)
    task_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
