"""Operaciones CRUD sobre la base de datos - device_systems (EV09).

Toda la interaccion con SQLAlchemy vive en esta capa; las rutas solo
reciben la sesion por inyeccion de dependencias y llaman a estas funciones.
"""

from typing import List, Optional

from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import (
    OrdenUsuarios,
    UserCreate,
    UserPatch,
    UserRole,
    UserUpdate,
)


def listar_usuarios(
    db: Session,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    order_by: OrdenUsuarios = OrdenUsuarios.NAME,
    descendente: bool = False,
) -> List[User]:
    """Lista usuarios aplicando filtros y ordenamiento."""
    consulta = select(User)

    if role is not None:
        consulta = consulta.where(User.role == role.value)

    if is_active is not None:
        consulta = consulta.where(User.is_active == is_active)

    columna = User.name if order_by == OrdenUsuarios.NAME else User.created_at
    consulta = consulta.order_by(desc(columna) if descendente else asc(columna))

    return list(db.execute(consulta).scalars().all())


def obtener_por_id(db: Session, user_id: int) -> Optional[User]:
    """Busca un usuario por su clave primaria."""
    return db.get(User, user_id)


def obtener_por_email(db: Session, email: str) -> Optional[User]:
    """Busca un usuario por su correo electronico."""
    consulta = select(User).where(User.email == email.lower())
    return db.execute(consulta).scalars().first()


def email_duplicado(db: Session, email: str, excluir_id: Optional[int] = None) -> bool:
    """Indica si el correo ya pertenece a otro usuario."""
    encontrado = obtener_por_email(db, email)
    if encontrado is None:
        return False
    return encontrado.id != excluir_id


def crear_usuario(db: Session, datos: UserCreate) -> User:
    """Inserta un usuario nuevo en la base de datos."""
    usuario = User(
        name=datos.name,
        email=str(datos.email).lower(),
        role=datos.role.value,
        is_active=datos.is_active,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def actualizar_usuario(db: Session, usuario: User, datos: UserUpdate) -> User:
    """Reemplaza todos los campos del usuario (PUT)."""
    usuario.name = datos.name
    usuario.email = str(datos.email).lower()
    usuario.role = datos.role.value
    usuario.is_active = datos.is_active

    db.commit()
    db.refresh(usuario)
    return usuario


def actualizar_parcial(db: Session, usuario: User, datos: UserPatch) -> User:
    """Actualiza solo los campos enviados por el cliente (PATCH)."""
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    for campo, valor in cambios.items():
        if campo == "role":
            setattr(usuario, campo, valor.value if isinstance(valor, UserRole) else valor)
        elif campo == "email":
            setattr(usuario, campo, str(valor).lower())
        else:
            setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario: User) -> None:
    """Elimina el usuario de la base de datos."""
    db.delete(usuario)
    db.commit()
