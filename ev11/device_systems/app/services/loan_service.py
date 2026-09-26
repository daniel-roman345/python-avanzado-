"""Gestion de prestamos y consultas con joins - device_systems (EV10)."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.device_schema import DeviceType
from app.schemas.loan_schema import LoanStatus


def ahora() -> datetime:
    """Fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


def _consulta_con_relaciones():
    """Consulta base de prestamos trayendo usuario y dispositivo (join)."""
    return select(Loan).options(
        joinedload(Loan.user), joinedload(Loan.device)
    )


def listar_prestamos(
    db: Session,
    status: Optional[LoanStatus] = None,
    user_id: Optional[int] = None,
    device_id: Optional[int] = None,
    user_email: Optional[str] = None,
    device_type: Optional[DeviceType] = None,
    search: Optional[str] = None,
) -> List[Loan]:
    """Lista prestamos combinando filtros sobre las tres tablas.

    Usa `join()` hacia `users` y `devices` solo cuando el filtro lo
    necesita, y condiciones multiples con `and_()` / `ilike()`.
    """
    consulta = _consulta_con_relaciones()
    condiciones = []

    if status is not None:
        condiciones.append(Loan.status == status.value)

    if user_id is not None:
        condiciones.append(Loan.user_id == user_id)

    if device_id is not None:
        condiciones.append(Loan.device_id == device_id)

    if user_email is not None:
        consulta = consulta.join(User, Loan.user_id == User.id)
        condiciones.append(User.email.ilike(f"%{user_email}%"))

    if device_type is not None or search is not None:
        consulta = consulta.join(Device, Loan.device_id == Device.id)

        if device_type is not None:
            condiciones.append(Device.device_type == device_type.value)

        if search is not None:
            condiciones.append(Device.name.ilike(f"%{search}%"))

    if condiciones:
        consulta = consulta.where(and_(*condiciones))

    consulta = consulta.order_by(Loan.loan_date.desc())
    return list(db.execute(consulta).unique().scalars().all())


def obtener_por_id(db: Session, loan_id: int) -> Optional[Loan]:
    """Busca un prestamo por su clave primaria, con sus relaciones."""
    consulta = _consulta_con_relaciones().where(Loan.id == loan_id)
    return db.execute(consulta).unique().scalars().first()


def prestamos_de_usuario(db: Session, user_id: int) -> List[Loan]:
    """Consulta con join: todos los prestamos de un usuario."""
    consulta = _consulta_con_relaciones().where(Loan.user_id == user_id)
    consulta = consulta.order_by(Loan.loan_date.desc())
    return list(db.execute(consulta).unique().scalars().all())


def prestamos_de_dispositivo(db: Session, device_id: int) -> List[Loan]:
    """Consulta con join: historial de prestamos de un dispositivo."""
    consulta = _consulta_con_relaciones().where(Loan.device_id == device_id)
    consulta = consulta.order_by(Loan.loan_date.desc())
    return list(db.execute(consulta).unique().scalars().all())


def crear_prestamo(db: Session, usuario: User, dispositivo: Device) -> Loan:
    """Registra el prestamo y marca el dispositivo como no disponible."""
    prestamo = Loan(
        user_id=usuario.id,
        device_id=dispositivo.id,
        loan_date=ahora(),
        status=LoanStatus.ACTIVE.value,
    )

    dispositivo.is_available = False

    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)
    return prestamo


def devolver_prestamo(db: Session, prestamo: Loan) -> Loan:
    """Marca el prestamo como devuelto y libera el dispositivo."""
    prestamo.status = LoanStatus.RETURNED.value
    prestamo.return_date = ahora()
    prestamo.device.is_available = True

    db.commit()
    db.refresh(prestamo)
    return prestamo


def cambiar_estado(db: Session, prestamo: Loan, status: LoanStatus) -> Loan:
    """Actualiza el estado del prestamo (por ejemplo a `overdue`)."""
    prestamo.status = status.value

    if status == LoanStatus.RETURNED and prestamo.return_date is None:
        prestamo.return_date = ahora()
        prestamo.device.is_available = True

    db.commit()
    db.refresh(prestamo)
    return prestamo
