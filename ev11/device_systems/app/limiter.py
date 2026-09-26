"""Instancia global del rate limiter - device_systems (EV11).

Se declara aqui para que las rutas puedan usar `@limiter.limit(...)`
sin importar `main.py` (evita imports circulares). El limiter se conecta
a la app en `app/main.py`.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
)
