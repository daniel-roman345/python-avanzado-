"""Modelos Pydantic v2 del recurso users - device_systems (EV08)."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(str, Enum):
    """Roles permitidos dentro de device_systems."""

    ADMIN = "admin"
    SUPPORT = "support"
    USER = "user"


class UserBase(BaseModel):
    """Campos comunes de entrada y salida."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=60,
        description="Nombre completo del usuario (minimo 3 caracteres)",
        examples=["Ana Perez"],
    )
    email: EmailStr = Field(
        ...,
        description="Correo electronico con formato valido",
        examples=["ana@sena.edu.co"],
    )
    role: UserRole = Field(
        ...,
        description="Rol del usuario: admin, support o user",
        examples=["admin"],
    )
    is_active: bool = Field(
        default=True,
        description="Indica si el usuario esta activo en el sistema",
    )

    @field_validator("name")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        """Elimina espacios sobrantes y evita nombres vacios."""
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
    """Entrada de PUT /users/{user_id}: reemplazo completo del usuario."""

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
    """Entrada de PATCH /users/{user_id}: todos los campos son opcionales."""

    name: Optional[str] = Field(default=None, min_length=3, max_length=60)
    email: Optional[EmailStr] = Field(default=None)
    role: Optional[UserRole] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)

    model_config = ConfigDict(
        json_schema_extra={"example": {"role": "support"}}
    )

    @field_validator("name")
    @classmethod
    def validar_nombre(cls, valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return valor
        limpio = valor.strip()
        if len(limpio) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres reales")
        return limpio


class UserResponse(UserBase):
    """Salida: expone solo los datos publicos del usuario."""

    id: int = Field(..., description="Identificador unico del usuario")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Respuesta estandarizada del listado de usuarios."""

    total: int = Field(..., description="Cantidad de usuarios devueltos")
    data: List[UserResponse] = Field(..., description="Usuarios encontrados")


class MessageResponse(BaseModel):
    """Respuesta simple con mensaje (usada por DELETE)."""

    message: str = Field(..., examples=["Usuario eliminado correctamente"])


class ErrorResponse(BaseModel):
    """Formato estructurado de error de device_systems."""

    error: bool = True
    message: str = Field(..., examples=["Usuario no encontrado"])
    status_code: int = Field(..., examples=[404])
