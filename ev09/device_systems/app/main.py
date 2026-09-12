"""Punto de entrada de la API device_systems (EV09).

Version 3.0.0: los usuarios dejan de vivir en memoria y se almacenan en
una base de datos relacional (SQLite) gestionada con SQLAlchemy.
"""

from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.database.connection import DATABASE_URL, crear_tablas
from app.routes import user_routes

APP_NAME = "device_systems"
API_VERSION = "3.0"

tags_metadata = [
    {
        "name": "Users",
        "description": (
            "CRUD completo del recurso **usuarios** persistido en base de datos."
        ),
    },
    {"name": "Root", "description": "Informacion general y estado de la API."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas de la base de datos al iniciar la aplicacion."""
    crear_tablas()
    yield


app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para la gestion de usuarios del sistema **device_systems**.\n\n"
        "### Novedades de esta version\n"
        "- Persistencia real con **SQLAlchemy** sobre **SQLite**.\n"
        "- Modelo `User` con constraints (`unique`, `nullable=False`).\n"
        "- Sesion de base de datos inyectada con `Depends(get_db)`.\n"
        "- CRUD completo, filtros y ordenamiento sobre la base de datos."
    ),
    version="3.0.0",
    contact={
        "name": "Daniel Roman - Aprendiz SENA",
        "email": "daniel992007@gmail.com",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)


@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    """Agrega las cabeceras propias de device_systems a toda respuesta."""
    response = await call_next(request)
    response.headers["X-App-Name"] = APP_NAME
    response.headers["X-API-Version"] = API_VERSION
    return response


@app.exception_handler(HTTPException)
async def manejar_http_exception(request: Request, exc: HTTPException):
    """Formato unico de error para toda la API."""
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
    """Estandariza los errores de validacion de Pydantic (422)."""
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
    """Traduce la violacion de un constraint de la base de datos a un 400."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": True,
            "message": "Violacion de una restriccion de la base de datos",
            "status_code": status.HTTP_400_BAD_REQUEST,
            "path": request.url.path,
        },
    )


app.include_router(user_routes.router)


@app.get(
    "/",
    tags=["Root"],
    summary="Informacion de la API",
    response_description="Datos generales de device_systems",
)
def raiz() -> Dict[str, str]:
    return {
        "app": APP_NAME,
        "version": API_VERSION,
        "database": DATABASE_URL,
        "docs": "/docs",
        "redoc": "/redoc",
        "recurso_principal": "/users",
    }


@app.get(
    "/health",
    tags=["Root"],
    summary="Estado del servicio",
    response_description="Estado actual de la API",
)
def health() -> Dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": API_VERSION}
