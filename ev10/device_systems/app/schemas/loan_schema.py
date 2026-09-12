"""Schemas Pydantic v2 del recurso loans - device_systems (EV10)."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.device_schema import DeviceMini


class LoanStatus(str, Enum):
    """Estados posibles de un prestamo."""

    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"


class UserMini(BaseModel):
    """Datos basicos del usuario usados en las consultas con join."""

    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class LoanCreate(BaseModel):
    """Entrada de POST /loans."""

    user_id: int = Field(..., ge=1, examples=[1])
    device_id: int = Field(..., ge=1, examples=[3])

    model_config = ConfigDict(
        json_schema_extra={"example": {"user_id": 1, "device_id": 3}}
    )


class LoanUpdate(BaseModel):
    """Entrada de PATCH /loans/{loan_id}: cambio de estado."""

    status: LoanStatus = Field(..., examples=["overdue"])

    model_config = ConfigDict(json_schema_extra={"example": {"status": "overdue"}})


class LoanResponse(BaseModel):
    """Salida basica de un prestamo."""

    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime]
    status: LoanStatus

    model_config = ConfigDict(from_attributes=True)


class LoanDetailResponse(BaseModel):
    """Salida de un prestamo con la informacion relacionada (join)."""

    loan_id: int = Field(..., validation_alias="id", serialization_alias="loan_id")
    status: LoanStatus
    loan_date: datetime
    return_date: Optional[datetime]
    user: UserMini
    device: DeviceMini

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LoanListResponse(BaseModel):
    """Respuesta estandarizada del listado de prestamos."""

    total: int
    data: List[LoanResponse]


class LoanDetailListResponse(BaseModel):
    """Respuesta estandarizada del listado de prestamos con detalle."""

    total: int
    data: List[LoanDetailResponse]
