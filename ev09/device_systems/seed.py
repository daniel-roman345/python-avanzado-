"""Carga datos de ejemplo en la base de datos - device_systems (EV09).

Uso:
    python seed.py
"""

from app.database.connection import SessionLocal, crear_tablas
from app.models.user_model import User

USUARIOS = [
    {"name": "Ana Perez", "email": "ana@sena.edu.co", "role": "admin", "is_active": True},
    {"name": "Carlos Gomez", "email": "carlos@sena.edu.co", "role": "support", "is_active": True},
    {"name": "Laura Martinez", "email": "laura@sena.edu.co", "role": "user", "is_active": False},
]


def main() -> None:
    crear_tablas()
    db = SessionLocal()

    try:
        creados = 0
        for datos in USUARIOS:
            existe = db.query(User).filter(User.email == datos["email"]).first()
            if existe is None:
                db.add(User(**datos))
                creados += 1
        db.commit()
        print(f"Usuarios insertados: {creados}")
        print(f"Total en la base de datos: {db.query(User).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
