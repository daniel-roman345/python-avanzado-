"""Operaciones CRUD y consultas del recurso devices - device_systems (EV10)."""

from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.schemas.device_schema import (
    DeviceCreate,
    DevicePatch,
    DeviceType,
    DeviceUpdate,
)


def listar_dispositivos(
    db: Session,
    device_type: Optional[DeviceType] = None,
    is_available: Optional[bool] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Device]:
    """Lista dispositivos aplicando filtros avanzados opcionales."""
    consulta = select(Device)

    if device_type is not None:
        consulta = consulta.where(Device.device_type == device_type.value)

    if is_available is not None:
        consulta = consulta.where(Device.is_available == is_available)

    if brand is not None:
        consulta = consulta.where(Device.brand.ilike(f"%{brand}%"))

    if search is not None:
        patron = f"%{search}%"
        consulta = consulta.where(
            or_(
                Device.name.ilike(patron),
                Device.serial_number.ilike(patron),
                Device.brand.ilike(patron),
            )
        )

    return list(db.execute(consulta.order_by(Device.name)).scalars().all())


def obtener_por_id(db: Session, device_id: int) -> Optional[Device]:
    """Busca un dispositivo por su clave primaria."""
    return db.get(Device, device_id)


def obtener_por_serial(db: Session, serial_number: str) -> Optional[Device]:
    """Busca un dispositivo por su numero de serie."""
    consulta = select(Device).where(Device.serial_number == serial_number.upper())
    return db.execute(consulta).scalars().first()


def serial_duplicado(
    db: Session, serial_number: str, excluir_id: Optional[int] = None
) -> bool:
    """Indica si el numero de serie ya pertenece a otro dispositivo."""
    encontrado = obtener_por_serial(db, serial_number)
    if encontrado is None:
        return False
    return encontrado.id != excluir_id


def crear_dispositivo(db: Session, datos: DeviceCreate) -> Device:
    """Inserta un dispositivo nuevo."""
    dispositivo = Device(
        name=datos.name,
        serial_number=datos.serial_number,
        device_type=datos.device_type.value,
        brand=datos.brand,
        is_available=datos.is_available,
    )

    db.add(dispositivo)
    db.commit()
    db.refresh(dispositivo)
    return dispositivo


def actualizar_dispositivo(
    db: Session, dispositivo: Device, datos: DeviceUpdate
) -> Device:
    """Reemplaza todos los campos del dispositivo (PUT)."""
    dispositivo.name = datos.name
    dispositivo.serial_number = datos.serial_number
    dispositivo.device_type = datos.device_type.value
    dispositivo.brand = datos.brand
    dispositivo.is_available = datos.is_available

    db.commit()
    db.refresh(dispositivo)
    return dispositivo


def actualizar_parcial(db: Session, dispositivo: Device, datos: DevicePatch) -> Device:
    """Actualiza solo los campos enviados (PATCH)."""
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    for campo, valor in cambios.items():
        if campo == "device_type":
            setattr(dispositivo, campo, valor.value if isinstance(valor, DeviceType) else valor)
        elif campo == "serial_number":
            setattr(dispositivo, campo, str(valor).strip().upper())
        else:
            setattr(dispositivo, campo, valor)

    db.commit()
    db.refresh(dispositivo)
    return dispositivo


def eliminar_dispositivo(db: Session, dispositivo: Device) -> None:
    """Elimina el dispositivo de la base de datos."""
    db.delete(dispositivo)
    db.commit()
