"""Configuracion cargada desde variables de entorno - device_systems (EV11)."""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Cargar el .env que este en la raiz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Contenedor de la configuracion global de la API."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./device_systems.db"
    )

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "cambia-esta-clave-en-produccion"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    CORS_ORIGINS: List[str] = [
        origen.strip()
        for origen in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
        ).split(",")
        if origen.strip()
    ]

    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")


settings = Settings()
