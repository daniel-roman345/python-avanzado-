"""Schemas Pydantic v2 del recurso devices - device_systems (EV10)."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeviceType(str, Enum):
    """Tipos de dispositivo permitidos."""

    LAPTOP = "laptop"
    TABLET = "tablet"
    PROYECTOR = "proyector"
    CAMARA = "camara"
    ROUTER = "router"
    MONITOR = "monitor"


class DeviceBase(BaseModel):
    """Campos comunes de entrada."""

    name: str = Field(..., min_length=3, max_length=80, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(..., min_length=3, max_length=50, examples=["LEN-2024-001"])
    device_type: DeviceType = Field(..., examples=["laptop"])
    brand: Optional[str] = Field(default=None, max_length=40, examples=["Lenovo"])
    is_available: bool = Field(default=True)

    @field_validator("serial_number")
    @classmethod
    def normalizar_serial(cls, valor: str) -> str:
        """El numero de serie se guarda en mayusculas y sin espacios."""
        limpio = valor.strip().upper()
        if len(limpio) < 3:
            raise ValueError("El numero de serie debe tener al menos 3 caracteres")
        return limpio


class DeviceCreate(DeviceBase):
    """Entrada de POST /devices."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Laptop Lenovo ThinkPad",
                "serial_number": "LEN-2024-001",
                "device_type": "laptop",
                "brand": "Lenovo",
                "is_available": True,
            }
        }
    )


class DeviceUpdate(DeviceBase):
    """Entrada de PUT /devices/{device_id}: reemplazo completo."""


class DevicePatch(BaseModel):
    """Entrada de PATCH /devices/{device_id}: campos opcionales."""

    name: Optional[str] = Field(default=None, min_length=3, max_length=80)
    serial_number: Optional[str] = Field(default=None, min_length=3, max_length=50)
    device_type: Optional[DeviceType] = None
    brand: Optional[str] = Field(default=None, max_length=40)
    is_available: Optional[bool] = None

    model_config = ConfigDict(json_schema_extra={"example": {"brand": "Lenovo"}})


class DeviceResponse(BaseModel):
    """Salida completa de un dispositivo."""

    id: int
    name: str
    serial_number: str
    device_type: DeviceType
    brand: Optional[str]
    is_available: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviceMini(BaseModel):
    """Datos basicos del dispositivo usados en las consultas con join."""

    id: int
    name: str
    serial_number: str
    device_type: DeviceType

    model_config = ConfigDict(from_attributes=True)


class DeviceListResponse(BaseModel):
    """Respuesta estandarizada del listado de dispositivos."""

    total: int
    data: List[DeviceResponse]
