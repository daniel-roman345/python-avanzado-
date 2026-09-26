"""Logica de negocio de autenticacion - device_systems (EV11)."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash, verify_password
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister


def obtener_por_email(db: Session, email: str) -> Optional[User]:
    """Busca un usuario por correo, en minuscula."""
    consulta = select(User).where(User.email == email.lower())
    return db.execute(consulta).scalars().first()


def email_registrado(db: Session, email: str) -> bool:
    """Indica si el correo ya existe en la base de datos."""
    return obtener_por_email(db, email) is not None


def registrar_usuario(db: Session, datos: UserRegister) -> User:
    """Crea un usuario con la contrasena hasheada con bcrypt.

    La contrasena en texto plano se descarta despues de generar el hash.
    """
    usuario = User(
        name=datos.name,
        email=str(datos.email).lower(),
        role=datos.role.value,
        is_active=True,
        hashed_password=get_password_hash(datos.password),
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, password: str) -> Optional[User]:
    """Devuelve el usuario si las credenciales son correctas, sino None."""
    usuario = obtener_por_email(db, email)
    if usuario is None:
        return None
    if not verify_password(password, usuario.hashed_password):
        return None
    return usuario
