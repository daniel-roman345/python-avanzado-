"""Simulacion de base de datos en memoria - device_systems (EV08)."""

from typing import Dict, List

users_db: List[Dict] = [
    {
        "id": 1,
        "name": "Ana Perez",
        "email": "ana@sena.edu.co",
        "role": "admin",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "Carlos Gomez",
        "email": "carlos@sena.edu.co",
        "role": "support",
        "is_active": True,
    },
    {
        "id": 3,
        "name": "Laura Martinez",
        "email": "laura@sena.edu.co",
        "role": "user",
        "is_active": False,
    },
]


def siguiente_id() -> int:
    """Calcula el proximo id disponible en la base en memoria."""
    if not users_db:
        return 1
    return max(usuario["id"] for usuario in users_db) + 1
