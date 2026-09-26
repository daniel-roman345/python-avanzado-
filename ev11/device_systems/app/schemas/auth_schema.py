"""Schemas Pydantic v2 de autenticacion - device_systems (EV11).

Validaciones avanzadas de contrasena y modelos de token JWT.
"""

import re
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.user_schema import UserRole

_PATRON_MAYUSCULA = re.compile(r"[A-Z]")
_PATRON_MINUSCULA = re.compile(r"[a-z]")
_PATRON_NUMERO = re.compile(r"\d")


def _validar_contrasena(valor: str) -> str:
    """Reglas obligatorias para las contrasenas de device_systems."""
    if len(valor) < 8:
        raise ValueError("La contrasena debe tener al menos 8 caracteres")
    if " " in valor:
        raise ValueError("La contrasena no puede contener espacios en blanco")
    if not _PATRON_MAYUSCULA.search(valor):
        raise ValueError("La contrasena debe tener al menos una letra mayuscula")
    if not _PATRON_MINUSCULA.search(valor):
        raise ValueError("La contrasena debe tener al menos una letra minuscula")
    if not _PATRON_NUMERO.search(valor):
        raise ValueError("La contrasena debe tener al menos un numero")
    return valor


class UserRegister(BaseModel):
    """Datos de entrada de `POST /auth/register`."""

    name: str = Field(..., min_length=3, max_length=60, examples=["Ana Perez"])
    email: EmailStr = Field(..., examples=["ana@sena.edu.co"])
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description=(
            "Minimo 8 caracteres, una mayuscula, una minuscula, un numero "
            "y sin espacios."
        ),
        examples=["Segura123"],
    )
    role: UserRole = Field(default=UserRole.USER, examples=["user"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Ana Perez",
                "email": "ana@sena.edu.co",
                "password": "Segura123",
                "role": "user",
            }
        }
    )

    @field_validator("name")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        limpio = valor.strip()
        if len(limpio) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres reales")
        return limpio

    @field_validator("password")
    @classmethod
    def validar_password(cls, valor: str) -> str:
        return _validar_contrasena(valor)


class UserLogin(BaseModel):
    """Datos de entrada de `POST /auth/login` (JSON)."""

    email: EmailStr = Field(..., examples=["ana@sena.edu.co"])
    password: str = Field(..., min_length=8, max_length=72, examples=["Segura123"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "ana@sena.edu.co", "password": "Segura123"}
        }
    )


class Token(BaseModel):
    """Respuesta de un login exitoso."""

    access_token: str = Field(..., description="JWT firmado con HS256")
    token_type: Literal["bearer"] = Field(default="bearer")
    expires_in: int = Field(..., description="Segundos de vida del token")


class TokenData(BaseModel):
    """Payload minimo que se guarda en el JWT."""

    sub: Optional[str] = None  # email del usuario
    user_id: Optional[int] = None
    role: Optional[str] = None
