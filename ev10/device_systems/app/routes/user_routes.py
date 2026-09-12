"""Endpoints del recurso users sobre base de datos - device_systems (EV10)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db, get_user_or_404
from app.models.user_model import User
from app.schemas.user_schema import (
    MessageResponse,
    OrdenUsuarios,
    UserCreate,
    UserListResponse,
    UserPatch,
    UserResponse,
    UserRole,
    UserUpdate,
)
from app.schemas.loan_schema import LoanDetailListResponse, LoanDetailResponse
from app.services import loan_service, user_service

router = APIRouter(prefix="/users", tags=["Users"])

RESPUESTA_404 = {404: {"description": "Usuario no encontrado"}}
RESPUESTA_400 = {400: {"description": "Solicitud invalida"}}


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description=(
        "Consulta los usuarios almacenados en la base de datos. Permite "
        "filtrar por `role` e `is_active` y ordenar por `name` o `created_at`."
    ),
    response_description="Listado de usuarios",
)
def listar_usuarios(
    response: Response,
    db: Session = Depends(get_db),
    role: Optional[UserRole] = Query(default=None, description="Filtra por rol"),
    is_active: Optional[bool] = Query(default=None, description="Filtra por estado"),
    order_by: OrdenUsuarios = Query(
        default=OrdenUsuarios.NAME, description="Campo de ordenamiento"
    ),
    desc: bool = Query(default=False, description="Orden descendente"),
) -> UserListResponse:
    usuarios = user_service.listar_usuarios(
        db, role=role, is_active=is_active, order_by=order_by, descendente=desc
    )
    response.headers["X-Total-Users"] = str(len(usuarios))
    return UserListResponse(
        total=len(usuarios),
        data=[UserResponse.model_validate(u) for u in usuarios],
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar usuario por ID",
    description="Obtiene un usuario de la base de datos por su identificador.",
    response_description="Usuario encontrado",
    responses=RESPUESTA_404,
)
def obtener_usuario(usuario: User = Depends(get_user_or_404)) -> UserResponse:
    return UserResponse.model_validate(usuario)


@router.get(
    "/{user_id}/loans",
    response_model=LoanDetailListResponse,
    status_code=status.HTTP_200_OK,
    summary="Prestamos de un usuario",
    description=(
        "Consulta con **join**: devuelve los prestamos del usuario junto "
        "con la informacion del dispositivo asociado."
    ),
    response_description="Prestamos del usuario",
    responses=RESPUESTA_404,
)
def prestamos_del_usuario(
    usuario: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> LoanDetailListResponse:
    prestamos = loan_service.prestamos_de_usuario(db, usuario.id)
    return LoanDetailListResponse(
        total=len(prestamos),
        data=[LoanDetailResponse.model_validate(p) for p in prestamos],
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un usuario",
    description=(
        "Registra un usuario en la base de datos validando los datos con "
        "Pydantic y comprobando que el correo no exista (constraint unique)."
    ),
    response_description="Usuario creado",
    responses={**RESPUESTA_400, 422: {"description": "Datos invalidos"}},
)
def crear_usuario(
    datos: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> UserResponse:
    if user_service.email_duplicado(db, str(datos.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )

    usuario = user_service.crear_usuario(db, datos)
    response.headers["Location"] = f"/users/{usuario.id}"
    return UserResponse.model_validate(usuario)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un usuario por completo",
    description="Reemplaza todos los campos del usuario en la base de datos.",
    response_description="Usuario actualizado",
    responses={**RESPUESTA_404, **RESPUESTA_400},
)
def actualizar_usuario(
    datos: UserUpdate,
    usuario: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> UserResponse:
    if user_service.email_duplicado(db, str(datos.email), excluir_id=usuario.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya pertenece a otro usuario",
        )

    actualizado = user_service.actualizar_usuario(db, usuario, datos)
    return UserResponse.model_validate(actualizado)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente un usuario",
    description=(
        "Modifica solo los campos enviados. Si el cuerpo llega vacio "
        "responde 400 Bad Request."
    ),
    response_description="Usuario actualizado parcialmente",
    responses={**RESPUESTA_404, **RESPUESTA_400},
)
def actualizar_usuario_parcial(
    datos: UserPatch,
    usuario: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> UserResponse:
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    if "email" in cambios and user_service.email_duplicado(
        db, str(datos.email), excluir_id=usuario.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya pertenece a otro usuario",
        )

    actualizado = user_service.actualizar_parcial(db, usuario, datos)
    return UserResponse.model_validate(actualizado)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar un usuario",
    description="Elimina el usuario de la base de datos.",
    response_description="Usuario eliminado correctamente",
    responses=RESPUESTA_404,
)
def eliminar_usuario(
    usuario: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> MessageResponse:
    user_id = usuario.id
    user_service.eliminar_usuario(db, usuario)
    return MessageResponse(message=f"Usuario {user_id} eliminado correctamente")
