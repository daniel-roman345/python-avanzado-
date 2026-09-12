"""Schemas Pydantic v2 del recurso users - device_systems (EV09).

Los schemas validan lo que entra y lo que sale de la API. El modelo
SQLAlchemy (`app/models/user_model.py`) representa la tabla; estos
schemas representan el contrato HTTP.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(str, Enum):
    """Roles permitidos dentro de device_systems."""

    ADMIN = "admin"
    SUPPORT = "support"
    USER = "user"


class OrdenUsuarios(str, Enum):
    """Campos por los que se puede ordenar el listado."""

    NAME = "name"
    CREATED_AT = "created_at"


class UserBase(BaseModel):
    """Campos comunes de entrada."""

    name: str = Field(..., min_length=3, max_length=60, examples=["Ana Perez"])
    email: EmailStr = Field(..., examples=["ana@sena.edu.co"])
    role: UserRole = Field(..., examples=["admin"])
    is_active: bool = Field(default=True)

    @field_validator("name")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        limpio = valor.strip()
        if len(limpio) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres reales")
        return limpio


class UserCreate(UserBase):
    """Entrada de POST /users."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Ana Perez",
                "email": "ana@sena.edu.co",
                "role": "admin",
                "is_active": True,
            }
        }
    )


class UserUpdate(UserBase):
    """Entrada de PUT /users/{user_id}: reemplazo completo."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Ana Maria Perez",
                "email": "ana.perez@sena.edu.co",
                "role": "support",
                "is_active": True,
            }
        }
    )


class UserPatch(BaseModel):
    """Entrada de PATCH /users/{user_id}: campos opcionales."""

    name: Optional[str] = Field(default=None, min_length=3, max_length=60)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(json_schema_extra={"example": {"role": "support"}})

    @field_validator("name")
    @classmethod
    def validar_nombre(cls, valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return valor
        limpio = valor.strip()
        if len(limpio) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres reales")
        return limpio


class UserResponse(BaseModel):
    """Salida de la API: se construye desde el modelo SQLAlchemy."""

    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Respuesta estandarizada del listado."""

    total: int
    data: List[UserResponse]


class MessageResponse(BaseModel):
    """Respuesta simple con mensaje."""

    message: str = Field(..., examples=["Usuario eliminado correctamente"])
