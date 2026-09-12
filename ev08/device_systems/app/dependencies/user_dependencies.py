"""Dependencias reutilizables con Depends() - device_systems (EV08)."""

from typing import Dict, Optional

from fastapi import Depends, Header, HTTPException, Path, status

from app.schemas.user_schema import UserCreate, UserPatch, UserRole, UserUpdate
from app.services import user_service

APP_NAME = "device_systems"
API_VERSION = "2.0"
API_KEY_DEMO = "device-systems-2024"


def get_api_settings() -> Dict[str, str]:
    """Entrega la configuracion general de la API."""
    return {
        "app_name": APP_NAME,
        "api_version": API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


def get_user_or_404(
    user_id: int = Path(..., ge=1, description="Identificador del usuario"),
) -> Dict:
    """Busca el usuario por ID y lanza 404 si no existe.

    Se reutiliza en GET, PUT, PATCH y DELETE por ID.
    """
    usuario = user_service.obtener_por_id(user_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return usuario


def validar_email_unico(usuario: UserCreate) -> UserCreate:
    """Evita crear dos usuarios con el mismo correo (POST)."""
    if user_service.email_duplicado(str(usuario.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )
    return usuario


def validar_email_unico_en_actualizacion(
    datos: UserUpdate,
    usuario_actual: Dict = Depends(get_user_or_404),
) -> UserUpdate:
    """Evita que un PUT deje dos usuarios con el mismo correo."""
    if user_service.email_duplicado(str(datos.email), excluir_id=usuario_actual["id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya pertenece a otro usuario",
        )
    return datos


def validar_patch_no_vacio(
    datos: UserPatch,
    usuario_actual: Dict = Depends(get_user_or_404),
) -> UserPatch:
    """Rechaza un PATCH sin datos y valida el correo si viene incluido."""
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    if "email" in cambios and user_service.email_duplicado(
        str(datos.email), excluir_id=usuario_actual["id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya pertenece a otro usuario",
        )

    return datos


def validar_rol_permitido(
    role: Optional[str] = None,
) -> Optional[UserRole]:
    """Valida manualmente el rol recibido como query parameter.

    Permite devolver un 400 propio en lugar del 422 automatico.
    """
    if role is None:
        return None

    try:
        return UserRole(role.lower())
    except ValueError:
        permitidos = ", ".join(r.value for r in UserRole)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol no permitido. Valores validos: {permitidos}",
        )


def verificar_api_key(
    x_api_key: Optional[str] = Header(
        default=None,
        description="Cabecera de autenticacion simulada (demo)",
    ),
) -> str:
    """Autenticacion basica simulada mediante cabecera HTTP."""
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta la cabecera X-API-Key",
        )

    if x_api_key != API_KEY_DEMO:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key invalida",
        )

    return x_api_key
