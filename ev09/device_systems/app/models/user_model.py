"""Modelo SQLAlchemy del recurso users - device_systems (EV09).

Este archivo define la tabla `users` de la base de datos. No debe
confundirse con los schemas Pydantic: aqui se declaran columnas,
tipos de datos y constraints.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


def ahora() -> datetime:
    """Fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


class User(Base):
    """Tabla users."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=ahora, nullable=False
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
