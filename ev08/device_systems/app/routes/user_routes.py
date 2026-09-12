"""Endpoints del recurso users - device_systems (EV08).

CRUD completo aplicando Dependency Injection, HTTPException y codigos de
estado HTTP adecuados.
"""

from typing import Dict, Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies.user_dependencies import (
    get_user_or_404,
    validar_email_unico,
    validar_email_unico_en_actualizacion,
    validar_patch_no_vacio,
    validar_rol_permitido,
)
from app.schemas.user_schema import (
    MessageResponse,
    UserCreate,
    UserListResponse,
    UserPatch,
    UserResponse,
    UserRole,
    UserUpdate,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

RESPUESTA_404 = {404: {"description": "Usuario no encontrado"}}
RESPUESTA_400 = {400: {"description": "Solicitud invalida"}}


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description=(
        "Lista los usuarios registrados. Admite los query parameters "
        "`role` (admin, support, user) e `is_active` (true/false)."
    ),
    response_description="Listado de usuarios encontrados",
    responses=RESPUESTA_400,
)
def listar_usuarios(
    response: Response,
    role: Optional[UserRole] = Depends(validar_rol_permitido),
    is_active: Optional[bool] = Query(
        default=None, description="Filtra por estado activo o inactivo"
    ),
) -> UserListResponse:
    usuarios = user_service.listar_usuarios(role=role, is_active=is_active)
    response.headers["X-Total-Users"] = str(len(usuarios))
    return UserListResponse(total=len(usuarios), data=usuarios)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar usuario por ID",
    description=(
        "Obtiene un usuario por su identificador. Usa la dependencia "
        "`get_user_or_404`, que lanza un 404 si el usuario no existe."
    ),
    response_description="Usuario encontrado",
    responses=RESPUESTA_404,
)
def obtener_usuario(usuario: Dict = Depends(get_user_or_404)) -> UserResponse:
    return UserResponse(**usuario)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un usuario",
    description=(
        "Registra un usuario nuevo. La dependencia `validar_email_unico` "
        "impide correos duplicados."
    ),
    response_description="Usuario creado correctamente",
    responses={**RESPUESTA_400, 422: {"description": "Datos invalidos"}},
)
def crear_usuario(
    response: Response,
    datos: UserCreate = Depends(validar_email_unico),
) -> UserResponse:
    nuevo = user_service.crear_usuario(datos)
    response.headers["Location"] = f"/users/{nuevo['id']}"
    return UserResponse(**nuevo)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un usuario por completo",
    description=(
        "Reemplaza toda la informacion del usuario. Requiere enviar "
        "`name`, `email`, `role` e `is_active`."
    ),
    response_description="Usuario actualizado",
    responses={**RESPUESTA_404, **RESPUESTA_400},
)
def actualizar_usuario(
    usuario: Dict = Depends(get_user_or_404),
    datos: UserUpdate = Depends(validar_email_unico_en_actualizacion),
) -> UserResponse:
    actualizado = user_service.actualizar_usuario(usuario, datos)
    return UserResponse(**actualizado)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente un usuario",
    description=(
        "Modifica solo los campos enviados. Si el cuerpo llega vacio la "
        "dependencia `validar_patch_no_vacio` responde 400 Bad Request."
    ),
    response_description="Usuario actualizado parcialmente",
    responses={**RESPUESTA_404, **RESPUESTA_400},
)
def actualizar_usuario_parcial(
    usuario: Dict = Depends(get_user_or_404),
    datos: UserPatch = Depends(validar_patch_no_vacio),
) -> UserResponse:
    actualizado = user_service.actualizar_parcial(usuario, datos)
    return UserResponse(**actualizado)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar un usuario",
    description=(
        "Elimina un usuario existente y confirma la operacion con un "
        "mensaje. Si el usuario no existe responde 404 Not Found."
    ),
    response_description="Usuario eliminado correctamente",
    responses=RESPUESTA_404,
)
def eliminar_usuario(usuario: Dict = Depends(get_user_or_404)) -> MessageResponse:
    user_service.eliminar_usuario(usuario)
    return MessageResponse(
        message=f"Usuario {usuario['id']} eliminado correctamente"
    )
