"""Modelo SQLAlchemy del recurso devices - device_systems (EV10)."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.loan_model import Loan


def ahora() -> datetime:
    """Fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


class Device(Base):
    """Tabla devices: equipos tecnologicos disponibles para prestamo."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    serial_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    device_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    brand: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=ahora, nullable=False
    )

    # Relacion One-to-Many: un dispositivo -> muchos prestamos historicos
    loans: Mapped[List["Loan"]] = relationship(
        "Loan",
        back_populates="device",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Device id={self.id} serial={self.serial_number}>"
