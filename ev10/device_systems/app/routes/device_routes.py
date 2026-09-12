"""Endpoints del recurso devices - device_systems (EV10)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db, get_device_or_404
from app.models.device_model import Device
from app.schemas.device_schema import (
    DeviceCreate,
    DeviceListResponse,
    DevicePatch,
    DeviceResponse,
    DeviceType,
    DeviceUpdate,
)
from app.schemas.loan_schema import LoanDetailListResponse, LoanDetailResponse
from app.services import device_service, loan_service

router = APIRouter(prefix="/devices", tags=["Devices"])

RESPUESTA_404 = {404: {"description": "Dispositivo no encontrado"}}
RESPUESTA_400 = {400: {"description": "Solicitud invalida"}}


@router.get(
    "",
    response_model=DeviceListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar dispositivos",
    description=(
        "Lista los dispositivos registrados. Admite filtros avanzados: "
        "`device_type`, `is_available`, `brand` (ilike) y `search` "
        "(busca en nombre, serial y marca)."
    ),
    response_description="Listado de dispositivos",
)
def listar_dispositivos(
    response: Response,
    db: Session = Depends(get_db),
    device_type: Optional[DeviceType] = Query(default=None, description="Tipo de dispositivo"),
    is_available: Optional[bool] = Query(default=None, description="Disponibilidad"),
    brand: Optional[str] = Query(default=None, description="Marca (busqueda parcial)"),
    search: Optional[str] = Query(default=None, description="Texto libre"),
) -> DeviceListResponse:
    dispositivos = device_service.listar_dispositivos(
        db,
        device_type=device_type,
        is_available=is_available,
        brand=brand,
        search=search,
    )
    response.headers["X-Total-Devices"] = str(len(dispositivos))
    return DeviceListResponse(
        total=len(dispositivos),
        data=[DeviceResponse.model_validate(d) for d in dispositivos],
    )


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar dispositivo por ID",
    response_description="Dispositivo encontrado",
    responses=RESPUESTA_404,
)
def obtener_dispositivo(dispositivo: Device = Depends(get_device_or_404)) -> DeviceResponse:
    return DeviceResponse.model_validate(dispositivo)


@router.get(
    "/{device_id}/loans",
    response_model=LoanDetailListResponse,
    status_code=status.HTTP_200_OK,
    summary="Historial de prestamos del dispositivo",
    description="Consulta con join: prestamos del dispositivo con usuario asociado.",
    response_description="Historial de prestamos",
    responses=RESPUESTA_404,
)
def prestamos_del_dispositivo(
    dispositivo: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> LoanDetailListResponse:
    prestamos = loan_service.prestamos_de_dispositivo(db, dispositivo.id)
    return LoanDetailListResponse(
        total=len(prestamos),
        data=[LoanDetailResponse.model_validate(p) for p in prestamos],
    )


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un dispositivo",
    description="Crea un dispositivo validando que el numero de serie sea unico.",
    response_description="Dispositivo creado",
    responses={**RESPUESTA_400, 422: {"description": "Datos invalidos"}},
)
def crear_dispositivo(
    datos: DeviceCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> DeviceResponse:
    if device_service.serial_duplicado(db, datos.serial_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El numero de serie ya esta registrado",
        )

    dispositivo = device_service.crear_dispositivo(db, datos)
    response.headers["Location"] = f"/devices/{dispositivo.id}"
    return DeviceResponse.model_validate(dispositivo)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un dispositivo por completo",
    response_description="Dispositivo actualizado",
    responses={**RESPUESTA_404, **RESPUESTA_400},
)
def actualizar_dispositivo(
    datos: DeviceUpdate,
    dispositivo: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> DeviceResponse:
    if device_service.serial_duplicado(db, datos.serial_number, excluir_id=dispositivo.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El numero de serie ya pertenece a otro dispositivo",
        )

    actualizado = device_service.actualizar_dispositivo(db, dispositivo, datos)
    return DeviceResponse.model_validate(actualizado)


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente un dispositivo",
    response_description="Dispositivo actualizado parcialmente",
    responses={**RESPUESTA_404, **RESPUESTA_400},
)
def actualizar_dispositivo_parcial(
    datos: DevicePatch,
    dispositivo: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> DeviceResponse:
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    if "serial_number" in cambios and device_service.serial_duplicado(
        db, str(datos.serial_number), excluir_id=dispositivo.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El numero de serie ya pertenece a otro dispositivo",
        )

    actualizado = device_service.actualizar_parcial(db, dispositivo, datos)
    return DeviceResponse.model_validate(actualizado)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un dispositivo",
    description=(
        "Elimina un dispositivo y responde 204 No Content (sin cuerpo). "
        "Si el dispositivo esta prestado (`is_available = false`) responde "
        "409 Conflict."
    ),
    response_description="Dispositivo eliminado correctamente",
    responses={**RESPUESTA_404, 409: {"description": "El dispositivo esta prestado"}},
)
def eliminar_dispositivo(
    dispositivo: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> Response:
    if not dispositivo.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un dispositivo que esta prestado",
        )

    device_service.eliminar_dispositivo(db, dispositivo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
