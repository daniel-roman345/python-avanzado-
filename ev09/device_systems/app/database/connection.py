"""Conexion con la base de datos - device_systems (EV09).

Configura el engine de SQLAlchemy, la fabrica de sesiones y la base
declarativa de la que heredan todos los modelos.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Base de datos SQLite para el desarrollo inicial
DATABASE_URL = "sqlite:///./device_systems.db"

# check_same_thread=False es necesario solo para SQLite con FastAPI
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
    """Crea las tablas de la base de datos si no existen."""
    # Importar los modelos registra las tablas en Base.metadata
    from app.models import user_model  # noqa: F401

    Base.metadata.create_all(bind=engine)
