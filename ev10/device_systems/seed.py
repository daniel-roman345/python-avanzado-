"""Carga datos de ejemplo en la base de datos - device_systems (EV10).

Ejecutar despues de aplicar las migraciones:
    alembic upgrade head
    python seed.py
"""

from app.database.connection import SessionLocal
from app.models.device_model import Device
from app.models.user_model import User

USUARIOS = [
    {"name": "Ana Perez", "email": "ana@sena.edu.co", "role": "admin", "is_active": True},
    {"name": "Carlos Gomez", "email": "carlos@sena.edu.co", "role": "support", "is_active": True},
    {"name": "Laura Martinez", "email": "laura@sena.edu.co", "role": "user", "is_active": False},
]

DISPOSITIVOS = [
    {
        "name": "Laptop Lenovo ThinkPad",
        "serial_number": "LEN-2024-001",
        "device_type": "laptop",
        "brand": "Lenovo",
    },
    {
        "name": "Tablet Samsung Galaxy Tab",
        "serial_number": "SAM-2024-014",
        "device_type": "tablet",
        "brand": "Samsung",
    },
    {
        "name": "Proyector Epson PowerLite",
        "serial_number": "EPS-2023-007",
        "device_type": "proyector",
        "brand": "Epson",
    },
    {
        "name": "Camara Canon EOS",
        "serial_number": "CAN-2023-021",
        "device_type": "camara",
        "brand": "Canon",
    },
]


def main() -> None:
    db = SessionLocal()

    try:
        for datos in USUARIOS:
            if db.query(User).filter(User.email == datos["email"]).first() is None:
                db.add(User(**datos))

        for datos in DISPOSITIVOS:
            existe = (
                db.query(Device)
                .filter(Device.serial_number == datos["serial_number"])
                .first()
            )
            if existe is None:
                db.add(Device(**datos))

        db.commit()
        print(f"Usuarios en la base de datos:     {db.query(User).count()}")
        print(f"Dispositivos en la base de datos: {db.query(Device).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
