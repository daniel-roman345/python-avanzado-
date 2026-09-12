"""Endpoints del recurso users - device_systems (EV07)."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query, Response, status

from app.schemas.user_schema import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserRole,
)

router = APIRouter(prefix="/users", tags=["Users"])

# "Base de datos" en memoria para esta primera version de device_systems
users_db: List[dict] = [
    {
        "id": 1,
        "name": "Ana Perez",
        "email": "ana@sena.edu.co",
        "role": "admin",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "Carlos Gomez",
        "email": "carlos@sena.edu.co",
        "role": "support",
        "is_active": True,
    },
    {
        "id": 3,
        "name": "Laura Martinez",
        "email": "laura@sena.edu.co",
        "role": "user",
        "is_active": False,
    },
]


def siguiente_id() -> int:
    """Calcula el proximo id disponible."""
    if not users_db:
        return 1
    return max(usuario["id"] for usuario in users_db) + 1


def email_registrado(email: str) -> bool:
    """Indica si un correo ya existe en la base en memoria."""
    return any(usuario["email"].lower() == email.lower() for usuario in users_db)


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description=(
        "Lista todos los usuarios registrados. Permite filtrar con query "
        "parameters por rol (`role`) y por estado (`is_active`)."
    ),
    response_description="Listado de usuarios encontrados",
)
def listar_usuarios(
    response: Response,
    role: Optional[UserRole] = Query(
        default=None,
        description="Filtra por rol: admin, support o user",
    ),
    is_active: Optional[bool] = Query(
        default=None,
        description="Filtra por estado activo (true) o inactivo (false)",
    ),
) -> UserListResponse:
    resultado = users_db

    if role is not None:
        resultado = [u for u in resultado if u["role"] == role.value]

    if is_active is not None:
        resultado = [u for u in resultado if u["is_active"] == is_active]

    response.headers["X-Total-Users"] = str(len(resultado))
    return UserListResponse(total=len(resultado), data=resultado)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar usuario por ID",
    description="Obtiene un usuario usando un path parameter.",
    response_description="Usuario encontrado",
    responses={404: {"description": "Usuario no encontrado"}},
)
def obtener_usuario(
    user_id: int = Path(..., ge=1, description="Identificador del usuario"),
) -> UserResponse:
    for usuario in users_db:
        if usuario["id"] == user_id:
            return UserResponse(**usuario)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado",
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description=(
        "Crea un usuario validando los datos con Pydantic v2 y evitando "
        "correos duplicados."
    ),
    response_description="Usuario creado correctamente",
    responses={
        400: {"description": "El correo ya esta registrado"},
        422: {"description": "Datos invalidos"},
    },
)
def crear_usuario(usuario: UserCreate, response: Response) -> UserResponse:
    if email_registrado(usuario.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )

    nuevo = {
        "id": siguiente_id(),
        "name": usuario.name,
        "email": str(usuario.email),
        "role": usuario.role.value,
        "is_active": usuario.is_active,
    }
    users_db.append(nuevo)

    response.headers["Location"] = f"/users/{nuevo['id']}"
    return UserResponse(**nuevo)
