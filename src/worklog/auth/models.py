from src.worklog.db.core import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, func
from datetime import datetime


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    phone: Mapped[str] = mapped_column(String(12), unique=True)
    password: Mapped[str] = mapped_column(String(256))

    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[str] = mapped_column(String(50))

    position: Mapped[str] = mapped_column(String(50), nullable=True)
    department_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    shift_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    role: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    chat_id_whatsapp: Mapped[str] = mapped_column(String(100), nullable=True)
    chat_id_telegram: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


