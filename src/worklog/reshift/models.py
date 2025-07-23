from src.worklog.db.core import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, Column
from datetime import datetime


class ReshiftUsers(Base):
    __tablename__ = 'reshift_users'

    id: Mapped[int] = Column(Integer, primary_key=True)

    first_user_id: Mapped[int] = Column(Integer, nullable=False)
    second_user_id: Mapped[int] = Column(Integer, nullable=False)

    created_at: Mapped[datetime] = Column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class Reshifts(Base):
    __tablename__ = 'reshifts'

    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, nullable=False)
    done: Mapped[str] = Column(String(255), nullable=False)
    todo: Mapped[str] = Column(String(255), nullable=False)

    created_at: Mapped[datetime] = Column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
