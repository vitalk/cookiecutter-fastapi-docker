from datetime import datetime
import uuid

from sqlalchemy import (
    DateTime,
    Identity,
    Integer,
    LargeBinary,
    String,
    UUID,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.database.declarative_base import Base


class User(Base):
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


__all__ = [model for model in locals() if isinstance(model, Base)]
