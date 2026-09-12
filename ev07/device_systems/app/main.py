"""Punto de entrada de la API device_systems (EV07).

API REST para la gestion de usuarios construida con FastAPI y Pydantic v2.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.routes import user_routes

APP_NAME = "device_systems"
API_VERSION = "1.0"

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para la gestion de usuarios del sistema **device_systems**.\n\n"
        "Incluye metodos GET y POST, path parameters, query parameters, "
        "validacion de datos con Pydantic v2, response models y cabeceras "
        "HTTP personalizadas."
    ),
    version="1.0.0",
    contact={
        "name": "Daniel Roman - Aprendiz SENA",
        "email": "daniel992007@gmail.com",
    },
    openapi_tags=[
        {
            "name": "Users",
            "description": "Operaciones sobre el recurso usuarios.",
        },
        {
            "name": "Root",
            "description": "Informacion general de la API.",
        },
    ],
)


@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    """Agrega cabeceras HTTP propias de device_systems a toda respuesta."""
    response = await call_next(request)
    response.headers["X-App-Name"] = APP_NAME
    response.headers["X-API-Version"] = API_VERSION
    return response


app.include_router(user_routes.router)


@app.get(
    "/",
    tags=["Root"],
    summary="Informacion de la API",
    response_description="Datos generales de device_systems",
)
def raiz() -> JSONResponse:
    """Devuelve informacion basica de la aplicacion."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "app": APP_NAME,
            "version": API_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "recurso_principal": "/users",
        },
    )
