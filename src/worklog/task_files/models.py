from src.worklog.db.core import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, func, Text
from datetime import datetime


class TaskFiles(Base):
    __tablename__ = 'task_files'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer)
    original_filename: Mapped[str] = mapped_column(String)
    new_filename: Mapped[str] = mapped_column(String)

    created_by: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

