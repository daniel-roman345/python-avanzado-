"""Modelo SQLAlchemy del recurso loans - device_systems (EV10).

Un prestamo relaciona un usuario con un dispositivo (Many-to-One hacia
ambos lados) y guarda el estado y las fechas de la operacion.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.device_model import Device
from app.models.user_model import User


def ahora() -> datetime:
    """Fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


class Loan(Base):
    """Tabla loans: prestamo de un dispositivo a un usuario."""

    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    loan_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=ahora, nullable=False
    )
    return_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False, index=True
    )

    # Relaciones Many-to-One
    user: Mapped[User] = relationship("User", back_populates="loans")
    device: Mapped[Device] = relationship("Device", back_populates="loans")

    def __repr__(self) -> str:
        return f"<Loan id={self.id} user={self.user_id} device={self.device_id} status={self.status}>"
