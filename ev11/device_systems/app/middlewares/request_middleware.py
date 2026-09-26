"""Middleware personalizado - device_systems (EV11).

Agrega a cada respuesta:

- `X-App-Name`: nombre de la aplicacion.
- `X-Process-Time`: tiempo de proceso en segundos.
- `X-Request-ID`: identificador unico para trazabilidad (correlation ID).

Ademas registra en el log `metodo ruta -> codigo (tiempo)`.
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

APP_NAME = "device_systems"

logger = logging.getLogger("device_systems.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Mide el tiempo de proceso, agrega cabeceras y registra el log."""

    async def dispatch(self, request: Request, call_next) -> Response:
        inicio = time.perf_counter()

        # Propaga X-Request-ID si viene del cliente, sino lo genera
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]

        try:
            response: Response = await call_next(request)
        except Exception:
            duracion = time.perf_counter() - inicio
            logger.exception(
                "%s %s -> 500 (%.4fs) [rid=%s]",
                request.method,
                request.url.path,
                duracion,
                request_id,
            )
            raise

        duracion = time.perf_counter() - inicio

        response.headers["X-App-Name"] = APP_NAME
        response.headers["X-Process-Time"] = f"{duracion:.4f}"
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "%s %s -> %d (%.4fs) [rid=%s]",
            request.method,
            request.url.path,
            response.status_code,
            duracion,
            request_id,
        )
        return response
