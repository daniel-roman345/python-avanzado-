"""Punto de entrada de la API device_systems (EV08).

Version 2.0.0: CRUD completo del recurso users, manejo profesional de
errores, codigos de estado HTTP, documentacion Swagger/OpenAPI y
Dependency Injection con Depends().
"""

from typing import Dict

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.dependencies.user_dependencies import (
    API_VERSION,
    APP_NAME,
    get_api_settings,
)
from app.routes import user_routes

tags_metadata = [
    {
        "name": "Users",
        "description": (
            "CRUD completo del recurso **usuarios**: listar, consultar, "
            "crear, actualizar (PUT y PATCH) y eliminar."
        ),
    },
    {
        "name": "Root",
        "description": "Informacion general y estado de la API.",
    },
]

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para la gestion de usuarios del sistema **device_systems**.\n\n"
        "### Caracteristicas de esta version\n"
        "- CRUD completo: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.\n"
        "- Manejo de errores con `HTTPException` y respuestas estructuradas.\n"
        "- Codigos de estado HTTP correctos en cada operacion.\n"
        "- Dependencias reutilizables con `Depends()`.\n"
        "- Documentacion automatica en `/docs` y `/redoc`."
    ),
    version="2.0.0",
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
    """Convierte los HTTPException en una respuesta de error estructurada."""
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


app.include_router(user_routes.router)


@app.get(
    "/",
    tags=["Root"],
    summary="Informacion de la API",
    description="Devuelve los metadatos generales de device_systems.",
    response_description="Datos generales de la API",
)
def raiz(config: Dict[str, str] = Depends(get_api_settings)) -> Dict[str, str]:
    """Usa la dependencia `get_api_settings` para entregar la configuracion."""
    return {**config, "recurso_principal": "/users"}


@app.get(
    "/health",
    tags=["Root"],
    summary="Estado del servicio",
    response_description="Estado actual de la API",
)
def health() -> Dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": API_VERSION}
