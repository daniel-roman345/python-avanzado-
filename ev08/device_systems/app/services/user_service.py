"""Logica de negocio del recurso users - device_systems (EV08).

Esta capa no conoce FastAPI: solo trabaja con la "base de datos" en memoria.
Las rutas son las encargadas de traducir los resultados a respuestas HTTP.
"""

from typing import Dict, List, Optional

from app.data.users_db import siguiente_id, users_db
from app.schemas.user_schema import UserCreate, UserPatch, UserRole, UserUpdate


def listar_usuarios(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
) -> List[Dict]:
    """Lista usuarios aplicando los filtros opcionales recibidos."""
    resultado = users_db

    if role is not None:
        resultado = [u for u in resultado if u["role"] == role.value]

    if is_active is not None:
        resultado = [u for u in resultado if u["is_active"] == is_active]

    return resultado


def obtener_por_id(user_id: int) -> Optional[Dict]:
    """Devuelve el usuario con ese id o None si no existe."""
    for usuario in users_db:
        if usuario["id"] == user_id:
            return usuario
    return None


def obtener_por_email(email: str) -> Optional[Dict]:
    """Devuelve el usuario con ese correo o None si no existe."""
    for usuario in users_db:
        if usuario["email"].lower() == email.lower():
            return usuario
    return None


def email_duplicado(email: str, excluir_id: Optional[int] = None) -> bool:
    """Indica si el correo ya pertenece a otro usuario."""
    encontrado = obtener_por_email(email)
    if encontrado is None:
        return False
    return encontrado["id"] != excluir_id


def crear_usuario(datos: UserCreate) -> Dict:
    """Agrega un usuario nuevo a la base en memoria."""
    nuevo = {
        "id": siguiente_id(),
        "name": datos.name,
        "email": str(datos.email),
        "role": datos.role.value,
        "is_active": datos.is_active,
    }
    users_db.append(nuevo)
    return nuevo


def actualizar_usuario(usuario: Dict, datos: UserUpdate) -> Dict:
    """Reemplaza por completo la informacion del usuario (PUT)."""
    usuario["name"] = datos.name
    usuario["email"] = str(datos.email)
    usuario["role"] = datos.role.value
    usuario["is_active"] = datos.is_active
    return usuario


def actualizar_parcial(usuario: Dict, datos: UserPatch) -> Dict:
    """Actualiza solo los campos enviados por el cliente (PATCH)."""
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    for campo, valor in cambios.items():
        if campo == "role":
            usuario[campo] = valor.value if isinstance(valor, UserRole) else valor
        elif campo == "email":
            usuario[campo] = str(valor)
        else:
            usuario[campo] = valor

    return usuario


def eliminar_usuario(usuario: Dict) -> None:
    """Elimina el usuario de la base en memoria."""
    users_db.remove(usuario)
