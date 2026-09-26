"""Endpoints del recurso users con proteccion por rol - device_systems (EV11).

Todas las rutas exigen JWT valido. Las mutaciones (POST, PUT, PATCH,
DELETE) requieren rol `admin`.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash
from app.dependencies.auth_dependency import (
    get_current_active_user,
    require_admin,
)
from app.dependencies.database_dependency import get_db, get_user_or_404
from app.limiter import limiter
from app.models.user_model import User
from app.schemas.loan_schema import LoanDetailListResponse, LoanDetailResponse
from app.schemas.user_schema import (
    OrdenUsuarios,
    UserAdminCreate,
    UserListResponse,
    UserPatch,
    UserResponse,
    UserRole,
    UserUpdate,
)
from app.services import loan_service, user_service

router = APIRouter(prefix="/users", tags=["Users"])

RESPUESTA_404 = {404: {"description": "Usuario no encontrado"}}
RESPUESTA_400 = {400: {"description": "Solicitud invalida"}}
RESPUESTA_401 = {401: {"description": "Token invalido o ausente"}}
RESPUESTA_403 = {403: {"description": "Rol insuficiente"}}


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios (autenticado)",
    description=(
        "Ruta protegida por JWT. Filtros: `role`, `is_active`. "
        "Ordenamiento: `name` o `created_at`."
    ),
    response_description="Listado de usuarios",
    responses={**RESPUESTA_401, 429: {"description": "Rate limit excedido"}},
)
@limiter.limit("30/minute")
def listar_usuarios(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _actual: User = Depends(get_current_active_user),
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
    summary="Consultar usuario por ID (autenticado)",
    response_description="Usuario encontrado",
    responses={**RESPUESTA_404, **RESPUESTA_401},
)
def obtener_usuario(
    usuario: User = Depends(get_user_or_404),
    _actual: User = Depends(get_current_active_user),
) -> UserResponse:
    return UserResponse.model_validate(usuario)


@router.get(
    "/{user_id}/loans",
    response_model=LoanDetailListResponse,
    status_code=status.HTTP_200_OK,
    summary="Prestamos de un usuario (autenticado)",
    description="Consulta con **join**: prestamos del usuario y dispositivo asociado.",
    response_description="Prestamos del usuario",
    responses={**RESPUESTA_404, **RESPUESTA_401},
)
def prestamos_del_usuario(
    usuario: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    _actual: User = Depends(get_current_active_user),
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
    summary="Crear un usuario (solo admin)",
    description=(
        "Endpoint administrativo: crea un usuario con contrasena obligatoria "
        "(se hashea con bcrypt). Para el registro publico usar `POST /auth/register`."
    ),
    response_description="Usuario creado",
    responses={**RESPUESTA_400, **RESPUESTA_401, **RESPUESTA_403,
               422: {"description": "Datos invalidos"}},
)
def crear_usuario(
    datos: UserAdminCreate,
    response: Response,
    db: Session = Depends(get_db),
    _actual: User = Depends(require_admin),
) -> UserResponse:
    if user_service.email_duplicado(db, str(datos.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )

    usuario = user_service.crear_usuario_admin(
        db, datos, hashed_password=get_password_hash(datos.password)
    )
    response.headers["Location"] = f"/users/{usuario.id}"
    return UserResponse.model_validate(usuario)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un usuario por completo (solo admin)",
    response_description="Usuario actualizado",
    responses={**RESPUESTA_404, **RESPUESTA_400, **RESPUESTA_401, **RESPUESTA_403},
)
def actualizar_usuario(
    datos: UserUpdate,
    usuario: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    _actual: User = Depends(require_admin),
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
    summary="Actualizar parcialmente un usuario (solo admin)",
    response_description="Usuario actualizado parcialmente",
    responses={**RESPUESTA_404, **RESPUESTA_400, **RESPUESTA_401, **RESPUESTA_403},
)
def actualizar_usuario_parcial(
    datos: UserPatch,
    usuario: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    _actual: User = Depends(require_admin),
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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario (solo admin)",
    response_description="Usuario eliminado correctamente",
    responses={**RESPUESTA_404, **RESPUESTA_401, **RESPUESTA_403},
)
def eliminar_usuario(
    usuario: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    _actual: User = Depends(require_admin),
) -> Response:
    user_service.eliminar_usuario(db, usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
