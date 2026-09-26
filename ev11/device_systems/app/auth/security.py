"""Utilidades de seguridad: hash de contrasenas y JWT - device_systems (EV11).

- Contrasenas: `bcrypt` mediante `passlib`.
- Tokens: JWT firmados con `HS256` mediante `python-jose`.

Ninguna contrasena en texto plano se guarda ni se retorna nunca.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Contexto de passlib con bcrypt como algoritmo principal
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt de la contrasena en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contrasena en texto plano con su hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Firma un JWT con la fecha de expiracion configurada."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    """Verifica la firma y retorna el payload del JWT.

    Lanza `JWTError` si el token es invalido o esta expirado.
    """
    return jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )


__all__ = [
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "JWTError",
]
