# device_systems — Persistencia con SQLAlchemy (EV09)

**Evidencia:** GA1-220501096-01-AA1-EV09 — FastAPI con SQLAlchemy
**Aprendiz:** Daniel Roman
**Version de la API:** 3.0.0

---

## 1. Descripcion de la API

En las versiones anteriores los usuarios de `device_systems` vivian en una lista en
memoria y se perdian al reiniciar el servidor. En esta version la API usa
**SQLAlchemy** sobre una base de datos **SQLite**, de modo que los usuarios se
crean, consultan, actualizan y eliminan **realmente en la base de datos**.

La API permite:

- Crear usuarios en base de datos (`POST`).
- Listar y consultar usuarios (`GET`).
- Filtrar por rol y por estado, y ordenar por nombre o fecha de creacion.
- Actualizar usuarios completa (`PUT`) y parcialmente (`PATCH`).
- Eliminar usuarios (`DELETE`).
- Validar los datos con **Pydantic v2** y aplicar **constraints** en el modelo.
- Manejar errores con codigos HTTP correctos.

## 2. Tecnologias utilizadas

| Tecnologia | Uso |
|---|---|
| FastAPI | Framework de la API REST |
| SQLAlchemy 2.x | ORM y acceso a la base de datos |
| SQLite | Motor de base de datos para desarrollo |
| Pydantic v2 | Validacion y schemas de entrada/salida |
| Uvicorn | Servidor ASGI |

## 3. Estructura del proyecto

```
device_systems/
│── app/
│   │── main.py                           # App, metadatos, middleware y manejo de errores
│   │
│   │── database/
│   │   │── connection.py                 # engine, SessionLocal, Base, crear_tablas()
│   │
│   │── models/
│   │   │── user_model.py                 # Modelo SQLAlchemy User (tabla users)
│   │
│   │── schemas/
│   │   │── user_schema.py                # Schemas Pydantic (Create/Update/Patch/Response)
│   │
│   │── routes/
│   │   │── user_routes.py                # Endpoints del recurso users
│   │
│   │── services/
│   │   │── user_service.py               # Operaciones CRUD y consultas
│   │
│   │── dependencies/
│   │   │── database_dependency.py        # get_db() y get_user_or_404()
│
│── capturas/
│── seed.py                               # Carga datos de ejemplo
│── requirements.txt
│── README.md
│── device_systems.db                     # Base de datos SQLite generada
```

## 4. Instalacion de dependencias

```bash
cd ev09/device_systems
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic email-validator
pip freeze > requirements.txt
```

O directamente:

```bash
pip install -r requirements.txt
```

## 5. Ejecucion

```bash
python seed.py
uvicorn app.main:app --reload
```

- `seed.py` crea las tablas e inserta 3 usuarios de ejemplo.
- Al arrancar, el evento `lifespan` de la app tambien ejecuta `crear_tablas()`,
  por lo que la base `device_systems.db` se genera sola.

| Recurso | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

## 6. Conexion con la base de datos

`app/database/connection.py`:

```python
DATABASE_URL = "sqlite:///./device_systems.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa de los modelos SQLAlchemy."""
```

## 7. Modelo SQLAlchemy `User` (tabla users)

| Campo | Tipo | Restriccion |
|---|---|---|
| `id` | `Integer` | Primary Key, indexado |
| `name` | `String(60)` | `nullable=False` |
| `email` | `String(120)` | `unique=True`, `nullable=False`, indexado |
| `role` | `String(20)` | `nullable=False` |
| `is_active` | `Boolean` | `default=True`, `nullable=False` |
| `created_at` | `DateTime` | `default=` fecha y hora actual |

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)
```

## 8. Diferencia entre modelo SQLAlchemy y schema Pydantic

| | Modelo SQLAlchemy (`User`) | Schema Pydantic (`UserCreate`, `UserResponse`...) |
|---|---|---|
| **Para que sirve** | Representa la **tabla** de la base de datos | Representa el **contrato HTTP** de entrada/salida |
| **Donde vive** | `app/models/user_model.py` | `app/schemas/user_schema.py` |
| **Que declara** | Columnas, tipos SQL, constraints, relaciones | Campos, tipos Python, validaciones y ejemplos |
| **Quien lo valida** | El motor de base de datos (`unique`, `nullable`) | Pydantic, antes de llegar a la base de datos |
| **Ejemplo de regla** | `email` con `unique=True` | `email: EmailStr` con formato valido |
| **Resultado si falla** | `IntegrityError` → `400` | `422 Unprocessable Entity` |

En resumen: **Pydantic valida la forma de los datos**; **SQLAlchemy valida y guarda
la integridad en la base**. El puente entre los dos es
`model_config = ConfigDict(from_attributes=True)`, que permite construir un
`UserResponse` directamente desde un objeto `User`:

```python
return UserResponse.model_validate(usuario)
```

## 9. Dependencia de base de datos

`app/dependencies/database_dependency.py`:

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Se inyecta en cada endpoint con `db: Session = Depends(get_db)`, garantizando que la
sesion **siempre** se cierre. La dependencia `get_user_or_404` la reutiliza para
buscar el usuario y lanzar `404` si no existe.

## 10. Operaciones CRUD implementadas (`app/services/user_service.py`)

| Funcion | Descripcion |
|---|---|
| `listar_usuarios(db, role, is_active, order_by, descendente)` | Lista con filtros y ordenamiento |
| `obtener_por_id(db, user_id)` | Busca por clave primaria |
| `obtener_por_email(db, email)` | Busca por correo |
| `email_duplicado(db, email, excluir_id)` | Verifica correos repetidos |
| `crear_usuario(db, datos)` | `add` + `commit` + `refresh` |
| `actualizar_usuario(db, usuario, datos)` | Actualizacion completa (PUT) |
| `actualizar_parcial(db, usuario, datos)` | Actualizacion parcial (PATCH) |
| `eliminar_usuario(db, usuario)` | `delete` + `commit` |

## 11. Tabla de endpoints

| Metodo | Endpoint | Descripcion | Codigo exitoso |
|---|---|---|---|
| `GET` | `/users` | Lista usuarios desde la base de datos | `200` |
| `GET` | `/users?role=admin` | Filtra por rol | `200` |
| `GET` | `/users?is_active=true` | Filtra por estado | `200` |
| `GET` | `/users?order_by=created_at&desc=true` | Ordena por fecha de creacion | `200` |
| `GET` | `/users/{user_id}` | Consulta por ID | `200` |
| `POST` | `/users` | Crea un usuario | `201` |
| `PUT` | `/users/{user_id}` | Actualiza todos los campos | `200` |
| `PATCH` | `/users/{user_id}` | Actualiza algunos campos | `200` |
| `DELETE` | `/users/{user_id}` | Elimina el usuario | `200` |

### Codigos de estado

| Caso | Codigo |
|---|---|
| Usuario creado | `201 Created` |
| Consulta correcta | `200 OK` |
| Actualizacion correcta | `200 OK` |
| Eliminacion correcta | `200 OK` (con mensaje) |
| Usuario no encontrado | `404 Not Found` |
| Email duplicado | `400 Bad Request` |
| PATCH sin datos | `400 Bad Request` |
| Error de validacion | `422 Unprocessable Entity` |

## 12. Ejemplos de peticiones y respuestas

### 12.1 POST /users

```bash
curl -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" -d "{\"name\":\"Pedro Ruiz\",\"email\":\"pedro@sena.edu.co\",\"role\":\"user\",\"is_active\":true}"
```

```json
HTTP 201 Created
{
  "id": 4,
  "name": "Pedro Ruiz",
  "email": "pedro@sena.edu.co",
  "role": "user",
  "is_active": true,
  "created_at": "2026-09-12T17:28:13.516784"
}
```

### 12.2 POST /users — correo duplicado

```json
HTTP 400
{ "error": true, "message": "El correo ya esta registrado", "status_code": 400, "path": "/users" }
```

### 12.3 GET /users

```json
HTTP 200
{
  "total": 3,
  "data": [
    { "id": 1, "name": "Ana Perez", "email": "ana@sena.edu.co", "role": "admin", "is_active": true, "created_at": "2026-09-12T17:28:06.151177" },
    { "id": 2, "name": "Carlos Gomez", "email": "carlos@sena.edu.co", "role": "support", "is_active": true, "created_at": "2026-09-12T17:28:06.151186" },
    { "id": 3, "name": "Laura Martinez", "email": "laura@sena.edu.co", "role": "user", "is_active": false, "created_at": "2026-09-12T17:28:06.151190" }
  ]
}
```

### 12.4 GET /users?role=admin

```json
{ "total": 1, "data": [ { "id": 1, "name": "Ana Perez", "role": "admin", "...": "..." } ] }
```

### 12.5 GET /users/99 — usuario inexistente

```json
HTTP 404
{ "error": true, "message": "Usuario no encontrado", "status_code": 404, "path": "/users/99" }
```

### 12.6 PUT /users/2

```json
HTTP 200
{ "id": 2, "name": "Carlos A Gomez", "email": "carlos.g@sena.edu.co", "role": "admin", "is_active": false, "created_at": "..." }
```

### 12.7 PATCH /users/3

Cuerpo: `{ "role": "support" }`

```json
HTTP 200
{ "id": 3, "name": "Laura Martinez", "email": "laura@sena.edu.co", "role": "support", "is_active": false, "created_at": "..." }
```

### 12.8 DELETE /users/4 y verificacion

```json
HTTP 200
{ "message": "Usuario 4 eliminado correctamente" }
```

```json
GET /users/4 -> HTTP 404
{ "error": true, "message": "Usuario no encontrado", "status_code": 404, "path": "/users/4" }
```

## 13. Pruebas funcionales realizadas

| # | Prueba | Esperado | Resultado |
|---|---|---|---|
| 1 | Crear un usuario valido | `201` | OK |
| 2 | Crear usuario con email repetido | `400` | OK |
| 3 | Listar usuarios | `200` | OK |
| 4 | Consultar usuario por ID | `200` | OK |
| 5 | Consultar usuario inexistente | `404` | OK |
| 6 | Filtrar por rol | `200` + 1 usuario | OK |
| 7 | Filtrar usuarios activos | `200` | OK |
| 8 | Ordenar por `created_at` descendente | `200` | OK |
| 9 | Actualizar con `PUT` | `200` | OK |
| 10 | `PUT` a usuario inexistente | `404` | OK |
| 11 | Actualizar parcialmente con `PATCH` | `200` | OK |
| 12 | `PATCH` vacio | `400` | OK |
| 13 | Eliminar con `DELETE` | `200` | OK |
| 14 | Verificar que el eliminado ya no exista | `404` | OK |
| 15 | Datos invalidos | `422` | OK |

## 14. Capturas

> Guarda las imagenes en `capturas/` con estos nombres.

| Evidencia | Captura |
|---|---|
| Estructura del proyecto | ![Estructura](capturas/01-estructura-proyecto.png) |
| Base de datos generada (tabla `users`) | ![BD](capturas/02-base-datos.png) |
| Swagger UI | ![Swagger](capturas/03-swagger-ui.png) |
| POST /users (201) | ![POST](capturas/04-post-users.png) |
| POST email duplicado (400) | ![Duplicado](capturas/05-post-email-duplicado.png) |
| GET /users | ![GET](capturas/06-get-users.png) |
| GET /users/{user_id} | ![GET id](capturas/07-get-user-id.png) |
| GET usuario inexistente (404) | ![404](capturas/08-get-user-404.png) |
| Filtro por rol | ![Rol](capturas/09-filtro-role.png) |
| Filtro por estado | ![Activos](capturas/10-filtro-activos.png) |
| PUT /users/{user_id} | ![PUT](capturas/11-put-user.png) |
| PATCH /users/{user_id} | ![PATCH](capturas/12-patch-user.png) |
| DELETE /users/{user_id} | ![DELETE](capturas/13-delete-user.png) |
| Verificacion del usuario eliminado | ![Verificacion](capturas/14-validar-eliminado.png) |

## 15. Reflexion final sobre la importancia de la persistencia

Trabajar con datos en memoria servia para entender los verbos HTTP, pero cualquier
reinicio borraba todo: la API no era utilizable en un escenario real. Al conectar
SQLAlchemy, `device_systems` paso a tener un estado que sobrevive a la aplicacion, y
eso cambio la forma de pensar el codigo.

Lo que mas me quedo claro es la separacion entre **modelo** y **schema**. El modelo
describe como se guarda la informacion (columnas, tipos, `unique`, `nullable`); el
schema describe como se comunica la API con el cliente. Gracias a
`from_attributes=True` convertir uno en otro es directo, y puedo exponer `created_at`
sin que el cliente tenga que enviarlo nunca.

Tambien entendi el valor de tener **dos capas de validacion**: Pydantic rechaza los
datos mal formados antes de tocar la base de datos, y los constraints de SQLAlchemy
protegen la integridad aunque el error venga de otro lado. Por eso agregue un manejador
de `IntegrityError` que traduce esa violacion a un `400` claro en lugar de un error 500.

Finalmente, la dependencia `get_db()` con `yield` me mostro como FastAPI administra
recursos: abre la sesion, la entrega al endpoint y la cierra siempre, incluso si ocurre
una excepcion. Esa es la base sobre la que en la siguiente evidencia se agregan
migraciones con Alembic y relaciones entre tablas.
