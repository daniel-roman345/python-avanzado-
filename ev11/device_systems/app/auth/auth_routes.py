"""Endpoints de autenticacion - device_systems (EV11).

- `POST /auth/register` -> registro con contrasena hasheada.
- `POST /auth/login` -> retorna un JWT (formato OAuth2PasswordRequestForm).
- `GET  /auth/me` -> perfil del usuario autenticado.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi.errors import RateLimitExceeded

from app.auth import auth_service
from app.auth.security import create_access_token
from app.config import settings
from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.limiter import limiter
from app.models.user_model import User
from app.schemas.auth_schema import Token, UserRegister
from app.schemas.user_schema import UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un usuario nuevo",
    description=(
        "Crea el usuario, hashea la contrasena con bcrypt y valida que "
        "sea segura (>=8, mayuscula, minuscula, numero, sin espacios)."
    ),
    response_description="Usuario creado (sin la contrasena)",
    responses={
        400: {"description": "Email ya registrado"},
        422: {"description": "Datos invalidos (contrasena debil, email invalido, etc.)"},
        429: {"description": "Demasiadas peticiones (rate limit)"},
    },
)
@limiter.limit("3/minute")
def registrar(
    request: Request,
    datos: UserRegister,
    db: Session = Depends(get_db),
) -> UserResponse:
    if auth_service.email_registrado(db, str(datos.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )

    usuario = auth_service.registrar_usuario(db, datos)
    return UserResponse.model_validate(usuario)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login OAuth2 y emision de JWT",
    description=(
        "Autentica con `username` (que aca es el email) y `password` en "
        "formato `application/x-www-form-urlencoded`. Devuelve un JWT "
        "firmado con HS256."
    ),
    response_description="Token JWT (access_token y expires_in en segundos)",
    responses={
        401: {"description": "Credenciales invalidas"},
        429: {"description": "Demasiadas peticiones (rate limit)"},
    },
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    usuario = auth_service.autenticar(db, form.username, form.password)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta esta desactivada",
        )

    minutos = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    token = create_access_token(
        data={
            "sub": usuario.email,
            "user_id": usuario.id,
            "role": usuario.role,
        },
        expires_delta=timedelta(minutes=minutos),
    )
    return Token(access_token=token, token_type="bearer", expires_in=minutos * 60)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Perfil del usuario autenticado",
    description="Devuelve los datos del usuario que envio el JWT.",
    response_description="Datos del usuario autenticado (sin la contrasena)",
    responses={401: {"description": "Token invalido o ausente"}},
)
def perfil(
    usuario: User = Depends(get_current_active_user),
) -> UserResponse:
    return UserResponse.model_validate(usuario)
