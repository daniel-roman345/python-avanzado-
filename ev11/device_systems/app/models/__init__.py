"""Modelos SQLAlchemy de device_systems.

Importar este paquete registra las tres tablas en `Base.metadata`, que es
lo que Alembic usa como `target_metadata` para autogenerar migraciones.
"""

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User

__all__ = ["User", "Device", "Loan"]
