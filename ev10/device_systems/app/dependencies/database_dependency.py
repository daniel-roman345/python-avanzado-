"""Dependencias de la aplicacion - device_systems (EV10)."""

from typing import Generator

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.services import device_service, loan_service, user_service


def get_db() -> Generator[Session, None, None]:
    """Entrega una sesion de base de datos y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_or_404(
    user_id: int = Path(..., ge=1, description="Identificador del usuario"),
    db: Session = Depends(get_db),
) -> User:
    """Busca el usuario o lanza 404."""
    usuario = user_service.obtener_por_id(db, user_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return usuario


def get_device_or_404(
    device_id: int = Path(..., ge=1, description="Identificador del dispositivo"),
    db: Session = Depends(get_db),
) -> Device:
    """Busca el dispositivo o lanza 404."""
    dispositivo = device_service.obtener_por_id(db, device_id)

    if dispositivo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado",
        )

    return dispositivo


def get_loan_or_404(
    loan_id: int = Path(..., ge=1, description="Identificador del prestamo"),
    db: Session = Depends(get_db),
) -> Loan:
    """Busca el prestamo (con usuario y dispositivo) o lanza 404."""
    prestamo = loan_service.obtener_por_id(db, loan_id)

    if prestamo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestamo no encontrado",
        )

    return prestamo
