"""Dependencias de autenticacion y autorizacion - device_systems (EV11).

Toda ruta protegida usa `get_current_user`. La autorizacion por roles se
implementa como *factory* (`require_roles`) para no repetir codigo.
"""

from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserRole

# tokenUrl = ruta que aparece en Swagger para el boton "Authorize"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decodifica el JWT y devuelve el usuario correspondiente.

    - 401 si el token es invalido, esta expirado o no existe.
    - 401 si el usuario del token ya no esta en la base de datos.
    """
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise credenciales_invalidas

    email = payload.get("sub")
    if not email:
        raise credenciales_invalidas

    usuario = db.query(User).filter(User.email == email).first()
    if usuario is None:
        raise credenciales_invalidas

    return usuario


def get_current_active_user(
    usuario: User = Depends(get_current_user),
) -> User:
    """Rechaza cuentas desactivadas con 403."""
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada",
        )
    return usuario


def require_roles(*roles_permitidos: UserRole):
    """Factory que crea una dependencia que exige uno de los roles dados."""
    permitidos = {rol.value for rol in roles_permitidos}

    def _dependencia(
        usuario: User = Depends(get_current_active_user),
    ) -> User:
        if usuario.role not in permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "No tienes permisos suficientes. Se requiere alguno de: "
                    + ", ".join(sorted(permitidos))
                ),
            )
        return usuario

    return _dependencia


# Dependencias listas para reusar en las rutas
require_admin = require_roles(UserRole.ADMIN)
require_admin_or_support = require_roles(UserRole.ADMIN, UserRole.SUPPORT)
require_any_role: Iterable[UserRole] = require_roles(
    UserRole.ADMIN, UserRole.SUPPORT, UserRole.USER
)
