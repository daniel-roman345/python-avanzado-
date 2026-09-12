"""Punto de entrada de la API device_systems (EV10).

Version 4.0.0: migraciones con Alembic, modelos relacionados
(User, Device, Loan) y consultas con joins y filtros avanzados.
"""

from typing import Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.database.connection import DATABASE_URL
from app.routes import device_routes, loan_routes, user_routes

APP_NAME = "device_systems"
API_VERSION = "4.0"

tags_metadata = [
    {
        "name": "Users",
        "description": "Gestion de **usuarios** y consulta de sus prestamos.",
    },
    {
        "name": "Devices",
        "description": (
            "Gestion de **dispositivos** tecnologicos disponibles para prestamo, "
            "con filtros por tipo, marca, disponibilidad y busqueda libre."
        ),
    },
    {
        "name": "Loans",
        "description": (
            "Gestion de **prestamos**: registro, devolucion y consultas con "
            "joins entre usuarios y dispositivos."
        ),
    },
    {"name": "Root", "description": "Informacion general y estado de la API."},
]

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para la gestion de usuarios, dispositivos y prestamos del "
        "sistema **device_systems**.\n\n"
        "### Novedades de esta version\n"
        "- Migraciones de base de datos con **Alembic**.\n"
        "- Modelos relacionados: `User` 1-N `Loan` N-1 `Device`.\n"
        "- Consultas con **joins** y filtros avanzados (`ilike`, `and_`, `or_`).\n"
        "- Reglas de negocio del prestamo y la devolucion de dispositivos."
    ),
    version="4.0.0",
    contact={
        "name": "Daniel Roman - Aprendiz SENA",
        "email": "daniel992007@gmail.com",
    },
    openapi_tags=tags_metadata,
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
        "recursos": ["/users", "/devices", "/loans"],
    }


@app.get(
    "/health",
    tags=["Root"],
    summary="Estado del servicio",
    response_description="Estado actual de la API",
)
def health() -> Dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": API_VERSION}
