"""Conexion con la base de datos - device_systems (EV11).

Configura el engine de SQLAlchemy, la fabrica de sesiones y la base
declarativa. La estructura de la base de datos se versiona con
**Alembic** (`alembic upgrade head`).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa de los modelos SQLAlchemy."""


def get_session() -> Session:
    """Devuelve una sesion nueva (uso interno o scripts)."""
    return SessionLocal()


def crear_tablas() -> None:
    """Crea las tablas sin Alembic (solo para pruebas rapidas).

    En esta evidencia la forma correcta de crear la estructura es
    ejecutar `alembic upgrade head`.
    """
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
