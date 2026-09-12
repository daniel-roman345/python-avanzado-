"""Dependencias de la aplicacion - device_systems (EV09)."""

from typing import Generator

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.user_model import User
from app.services import user_service


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
    """Busca el usuario en la base de datos o lanza 404."""
    usuario = user_service.obtener_por_id(db, user_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return usuario
