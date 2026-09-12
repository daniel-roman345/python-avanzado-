"""Endpoints del recurso loans - device_systems (EV10).

Incluye la gestion de prestamos y las consultas con joins y filtros
avanzados entre las tablas users, devices y loans.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db, get_loan_or_404
from app.models.loan_model import Loan
from app.schemas.device_schema import DeviceType
from app.schemas.loan_schema import (
    LoanCreate,
    LoanDetailListResponse,
    LoanDetailResponse,
    LoanListResponse,
    LoanResponse,
    LoanStatus,
    LoanUpdate,
)
from app.services import device_service, loan_service, user_service

router = APIRouter(prefix="/loans", tags=["Loans"])

RESPUESTA_404 = {404: {"description": "Recurso no encontrado"}}
RESPUESTA_409 = {409: {"description": "Regla de negocio incumplida"}}


def _filtros_comunes(
    db: Session,
    status_: Optional[LoanStatus],
    user_id: Optional[int],
    device_id: Optional[int],
    user_email: Optional[str],
    device_type: Optional[DeviceType],
    search: Optional[str],
):
    return loan_service.listar_prestamos(
        db,
        status=status_,
        user_id=user_id,
        device_id=device_id,
        user_email=user_email,
        device_type=device_type,
        search=search,
    )


@router.get(
    "",
    response_model=LoanListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar prestamos",
    description=(
        "Lista los prestamos registrados. Filtros disponibles: `status`, "
        "`user_id`, `device_id`, `user_email` (join con users), "
        "`device_type` y `search` (join con devices)."
    ),
    response_description="Listado de prestamos",
)
def listar_prestamos(
    response: Response,
    db: Session = Depends(get_db),
    status_filtro: Optional[LoanStatus] = Query(
        default=None, alias="status", description="Estado del prestamo"
    ),
    user_id: Optional[int] = Query(default=None, ge=1, description="ID del usuario"),
    device_id: Optional[int] = Query(default=None, ge=1, description="ID del dispositivo"),
    user_email: Optional[str] = Query(default=None, description="Correo del usuario"),
    device_type: Optional[DeviceType] = Query(default=None, description="Tipo de dispositivo"),
    search: Optional[str] = Query(default=None, description="Nombre del dispositivo"),
) -> LoanListResponse:
    prestamos = _filtros_comunes(
        db, status_filtro, user_id, device_id, user_email, device_type, search
    )
    response.headers["X-Total-Loans"] = str(len(prestamos))
    return LoanListResponse(
        total=len(prestamos),
        data=[LoanResponse.model_validate(p) for p in prestamos],
    )


@router.get(
    "/details",
    response_model=LoanDetailListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar prestamos con informacion relacionada",
    description=(
        "Consulta con **joins**: devuelve cada prestamo junto con los datos "
        "basicos del usuario y del dispositivo. Acepta los mismos filtros "
        "que `GET /loans`."
    ),
    response_description="Prestamos con usuario y dispositivo",
)
def listar_prestamos_detallados(
    db: Session = Depends(get_db),
    status_filtro: Optional[LoanStatus] = Query(default=None, alias="status"),
    user_id: Optional[int] = Query(default=None, ge=1),
    device_id: Optional[int] = Query(default=None, ge=1),
    user_email: Optional[str] = Query(default=None),
    device_type: Optional[DeviceType] = Query(default=None),
    search: Optional[str] = Query(default=None),
) -> LoanDetailListResponse:
    prestamos = _filtros_comunes(
        db, status_filtro, user_id, device_id, user_email, device_type, search
    )
    return LoanDetailListResponse(
        total=len(prestamos),
        data=[LoanDetailResponse.model_validate(p) for p in prestamos],
    )


@router.get(
    "/{loan_id}",
    response_model=LoanDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar un prestamo por ID",
    description="Devuelve el prestamo con la informacion del usuario y del dispositivo.",
    response_description="Prestamo encontrado",
    responses=RESPUESTA_404,
)
def obtener_prestamo(prestamo: Loan = Depends(get_loan_or_404)) -> LoanDetailResponse:
    return LoanDetailResponse.model_validate(prestamo)


@router.post(
    "",
    response_model=LoanDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un prestamo",
    description=(
        "Crea un prestamo validando que el usuario exista, que el dispositivo "
        "exista y que este disponible. Al crearlo, el dispositivo pasa a "
        "`is_available = false`."
    ),
    response_description="Prestamo creado",
    responses={**RESPUESTA_404, **RESPUESTA_409},
)
def crear_prestamo(
    datos: LoanCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> LoanDetailResponse:
    usuario = user_service.obtener_por_id(db, datos.user_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    dispositivo = device_service.obtener_por_id(db, datos.device_id)
    if dispositivo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado",
        )

    if not dispositivo.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El dispositivo no esta disponible",
        )

    prestamo = loan_service.crear_prestamo(db, usuario, dispositivo)
    response.headers["Location"] = f"/loans/{prestamo.id}"
    return LoanDetailResponse.model_validate(prestamo)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar la devolucion de un prestamo",
    description=(
        "Marca el prestamo como `returned`, asigna la fecha de devolucion y "
        "vuelve a dejar el dispositivo disponible. Si el prestamo ya fue "
        "devuelto responde 409 Conflict."
    ),
    response_description="Prestamo devuelto",
    responses={**RESPUESTA_404, **RESPUESTA_409},
)
def devolver_prestamo(
    prestamo: Loan = Depends(get_loan_or_404),
    db: Session = Depends(get_db),
) -> LoanDetailResponse:
    if prestamo.status == LoanStatus.RETURNED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El prestamo ya fue devuelto",
        )

    devuelto = loan_service.devolver_prestamo(db, prestamo)
    return LoanDetailResponse.model_validate(devuelto)


@router.patch(
    "/{loan_id}",
    response_model=LoanDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar el estado de un prestamo",
    description="Permite marcar un prestamo como `active`, `returned` u `overdue`.",
    response_description="Prestamo actualizado",
    responses=RESPUESTA_404,
)
def actualizar_prestamo(
    datos: LoanUpdate,
    prestamo: Loan = Depends(get_loan_or_404),
    db: Session = Depends(get_db),
) -> LoanDetailResponse:
    actualizado = loan_service.cambiar_estado(db, prestamo, datos.status)
    return LoanDetailResponse.model_validate(actualizado)
