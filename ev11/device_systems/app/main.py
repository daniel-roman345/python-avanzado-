"""Punto de entrada de la API device_systems (EV11).

Version 5.0.0: seguridad completa (OAuth2 + JWT, hash con passlib,
CORS, middleware personalizado, rate limiting, validaciones avanzadas
con Pydantic v2) sobre la base de EV10 (Alembic + relaciones + joins).
"""

import logging
from typing import Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import IntegrityError

from app.auth.auth_routes import router as auth_router
from app.config import settings
from app.database.connection import DATABASE_URL
from app.limiter import limiter
from app.middlewares.request_middleware import RequestContextMiddleware
from app.routes import device_routes, loan_routes, user_routes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

APP_NAME = "device_systems"
API_VERSION = "5.0"

tags_metadata = [
    {
        "name": "Auth",
        "description": (
            "**Autenticacion**: registro, login OAuth2 y perfil (`/auth/me`). "
            "Emision de JWT firmados con HS256."
        ),
    },
    {
        "name": "Users",
        "description": "Gestion de usuarios (rutas privadas, requiere token).",
    },
    {
        "name": "Devices",
        "description": (
            "Gestion de dispositivos. Crear/editar requiere rol `admin` o "
            "`support`; eliminar requiere `admin`."
        ),
    },
    {
        "name": "Loans",
        "description": (
            "Gestion de prestamos con reglas de negocio (disponibilidad, "
            "devolucion). Consultas con joins protegidas por rol."
        ),
    },
    {"name": "Root", "description": "Informacion general y estado de la API."},
]

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST **segura** para la gestion de usuarios, dispositivos y "
        "prestamos.\n\n"
        "### Seguridad de esta version\n"
        "- Autenticacion OAuth2 con tokens JWT (HS256).\n"
        "- Hash de contrasenas con bcrypt (passlib).\n"
        "- Autorizacion por roles (`admin`, `support`, `user`).\n"
        "- Middleware con X-App-Name, X-Process-Time y X-Request-ID.\n"
        "- CORS con lista blanca configurable via `.env`.\n"
        "- Rate limiting con `slowapi`.\n"
        "- Validaciones avanzadas de contrasena con Pydantic v2.\n"
    ),
    version="5.0.0",
    contact={
        "name": "Daniel Roman - Aprendiz SENA",
        "email": "daniel992007@gmail.com",
    },
    openapi_tags=tags_metadata,
)

# --- Rate limiter (slowapi) ---------------------------------------------------
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": True,
            "message": f"Limite de peticiones excedido: {exc.detail}",
            "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
            "path": request.url.path,
        },
    )


# --- CORS ---------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-App-Name", "X-Process-Time", "X-Request-ID"],
)

# --- Middleware personalizado (metricas y trazabilidad) -----------------------
app.add_middleware(RequestContextMiddleware)


# --- Manejadores de errores globales ------------------------------------------
@app.exception_handler(HTTPException)
async def manejar_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
        },
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Error de validacion en los datos enviados",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "detail": [
                {
                    "campo": ".".join(str(parte) for parte in error["loc"]),
                    "mensaje": error["msg"],
                }
                for error in exc.errors()
            ],
        },
    )


@app.exception_handler(IntegrityError)
async def manejar_error_integridad(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": True,
            "message": "Violacion de una restriccion de la base de datos",
            "status_code": status.HTTP_400_BAD_REQUEST,
            "path": request.url.path,
        },
    )


# --- Routers ------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(user_routes.router)
app.include_router(device_routes.router)
app.include_router(loan_routes.router)


@app.get(
    "/",
    tags=["Root"],
    summary="Informacion de la API",
    response_description="Datos generales de device_systems",
)
def raiz() -> Dict[str, object]:
    return {
        "app": APP_NAME,
        "version": API_VERSION,
        "database": DATABASE_URL,
        "docs": "/docs",
        "redoc": "/redoc",
        "recursos": ["/auth", "/users", "/devices", "/loans"],
        "seguridad": ["OAuth2", "JWT (HS256)", "bcrypt", "CORS", "rate-limit"],
    }


@app.get(
    "/health",
    tags=["Root"],
    summary="Estado del servicio",
    response_description="Estado actual de la API",
)
def health() -> Dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": API_VERSION}
