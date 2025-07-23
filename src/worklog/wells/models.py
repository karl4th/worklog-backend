from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, Integer, Float, Boolean

from src.worklog.db.core import Base


class Wells(Base):
    __tablename__ = 'wells'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    block_id: Mapped[int] = mapped_column(Integer, nullable=False)
    depth: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(255), nullable=False)

    out: Mapped[bool] = mapped_column(Boolean, nullable=False)
