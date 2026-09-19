# Guia de defensa oral - device_systems (EV07 a EV10)

Documento personal para navegar el proyecto en vivo, ubicar cualquier parte
del codigo al instante y justificar cada decision tecnica ante el instructor.
Cada actividad tiene: como se corre, estructura, archivo por archivo, decisiones
clave y preguntas tipicas del profe con la respuesta corta lista.

---

## 0. Lo primero: como demostrar cada actividad corriendo

Todas las actividades se corren igual, cambia solo la carpeta.

```bash
cd evNN/device_systems           # NN = 07, 08, 09 o 10
python -m venv .venv
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abrir en el navegador:

| Ruta | Para que |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger UI (probar endpoints en vivo) |
| `http://127.0.0.1:8000/redoc` | Documentacion ReDoc |
| `http://127.0.0.1:8000/openapi.json` | Esquema OpenAPI |

En EV09 y EV10, primero se crea la base de datos:

- **EV09**: la aplicacion crea las tablas sola al arrancar (evento `lifespan`
  llama a `crear_tablas()`). Tambien esta `python seed.py` para insertar
  usuarios de ejemplo.
- **EV10**: se usa Alembic. Los comandos son:

  ```bash
  alembic history                # muestra las 2 migraciones
  alembic upgrade head           # aplica todas las migraciones
  alembic current                # muestra la revision aplicada
  ```

  Luego `python seed.py` (crea 3 usuarios y 5 dispositivos de ejemplo) y
  `uvicorn app.main:app --reload`.

---

## 1. EV07 - Fundamentos de FastAPI (v1.0.0)

**Objetivo:** primera version de la API con GET, POST, path/query parameters,
validacion Pydantic v2, response models y cabeceras HTTP personalizadas.
Los datos se guardan en una lista en memoria.

### 1.1 Estructura

```
ev07/device_systems/
├── app/
│   ├── main.py              # crea la app, metadatos y middleware
│   ├── schemas/
│   │   └── user_schema.py   # modelos Pydantic
│   └── routes/
│       └── user_routes.py   # endpoints GET y POST
├── requirements.txt
└── README.md
```

**Por que esta estructura:** separar `schemas` (validacion) de `routes`
(endpoints) es el patron minimo recomendado por FastAPI. El instructor
seguramente pregunta por que no todo en un `main.py`: porque cuando
crece el proyecto (EV08 - EV10) se agregan mas capas y la separacion ya
esta lista.

### 1.2 `app/main.py` (linea por linea de las importantes)

- Linea 14: `app = FastAPI(...)` con `title`, `description`, `version` y
  `contact` -> esto alimenta la documentacion Swagger.
- Linea 27: `openapi_tags` -> agrupa los endpoints en Swagger. Aca hay 2
  tags: `Users` y `Root`.
- Linea 40: `@app.middleware("http")` -> el **middleware** que agrega las
  cabeceras `X-App-Name` y `X-API-Version` a **todas** las respuestas.
- Linea 49: `app.include_router(user_routes.router)` -> registra los
  endpoints del recurso users.
- Linea 52: endpoint raiz `GET /` que devuelve informacion general.

**Por que un middleware para las cabeceras:** un middleware corre en toda
peticion sin tener que repetir la cabecera en cada endpoint (principio DRY).
Ademas, el instructor puede preguntar por que no un decorador: porque las
cabeceras deben aplicar a **todas** las respuestas, incluidas las de error.

### 1.3 `app/schemas/user_schema.py`

Modelos que valida Pydantic v2:

- **`UserRole`** (`Enum`, linea 9): admin, support, user. Se declara como
  `str, Enum` para que quede como texto en el JSON. **Por que un Enum**:
  cualquier otro valor da 422 automatico, sin tener que escribir `if`.
- **`UserBase`** (linea 17): campos comunes. Reglas por campo:
  - `name`: `Field(min_length=3, max_length=60)`.
  - `email`: `EmailStr` -> valida formato con la libreria `email-validator`.
  - `role`: `UserRole`.
  - `is_active`: `bool` con `default=True`.
- **`@field_validator("name")`** (linea 42): validador personalizado.
  **Por que:** `Field(min_length=3)` cuenta espacios, entonces `"  a "`
  pasaria. Este validador hace `strip()` y vuelve a comprobar longitud.
- **`UserCreate`** (linea 52): hereda `UserBase`. Modelo de **entrada** del POST.
- **`UserResponse`** (linea 67): hereda `UserBase` y agrega `id`. Modelo de
  **salida**. **Por que separar UserCreate y UserResponse:** el cliente
  no envia el `id` cuando crea, pero la API debe devolverlo. Ademas, si en
  el futuro se agrega `password_hash`, no se expondria porque el `Response`
  no lo tiene.
- **`UserListResponse`** (linea 75): envuelve la lista en `{total, data}`
  para estandarizar la respuesta.

### 1.4 `app/routes/user_routes.py`

- `users_db` (linea 17): lista de diccionarios en memoria. Aca esta la
  "base de datos" simulada.
- `siguiente_id()` (linea 42): calcula `max(id) + 1` para generar el
  proximo id sin colisiones.
- `email_registrado()` (linea 49): busca por correo (case-insensitive con
  `.lower()`).
- `GET /users` (linea 54):
  - Recibe `role: Optional[UserRole] = Query(...)` y
    `is_active: Optional[bool] = Query(...)` -> **query parameters**.
  - `response: Response` es un parametro especial de FastAPI para
    manipular la cabecera de salida (`X-Total-Users`).
  - Filtra en memoria con listas por comprension.
- `GET /users/{user_id}` (linea 88):
  - `user_id: int = Path(..., ge=1)` -> **path parameter** con validacion
    de que sea >= 1.
  - Si no existe: `raise HTTPException(404, "Usuario no encontrado")`.
- `POST /users` (linea 110):
  - `usuario: UserCreate` -> el body es validado por Pydantic.
  - Verifica `email_registrado` y responde 400 si existe.
  - Responde 201 y agrega la cabecera `Location: /users/{id}`.

### 1.5 Preguntas tipicas EV07 y respuesta corta

- **"¿Donde valida el email?"** -> `EmailStr` en `user_schema.py:27`.
- **"¿Donde limita el nombre a >= 3?"** -> `Field(min_length=3)` en
  `user_schema.py:22` y el validador `validar_nombre` en la linea 42.
- **"¿Como filtras por rol?"** -> query parameter tipado como `UserRole` en
  `user_routes.py:67`, y se aplica en la linea 79 con comprension.
- **"¿Como devuelves cabeceras personalizadas?"** -> middleware
  `agregar_cabeceras_personalizadas` en `main.py:40`.
- **"¿Por que 400 en correo duplicado y no 409?"** -> la guia pide 400
  Bad Request; 409 Conflict tambien seria correcto, pero se siguio la
  tabla de codigos del documento.
- **"¿Como evitas correos repetidos?"** -> funcion `email_registrado`
  (`user_routes.py:49`) que compara en minusculas para no dejar pasar
  variantes de mayusculas.

---

## 2. EV08 - CRUD completo, errores y Dependency Injection (v2.0.0)

**Objetivo:** agregar PUT, PATCH, DELETE, manejar errores con
`HTTPException`, respuestas estructuradas, codigos HTTP correctos y
reutilizar logica con `Depends()`.

### 2.1 Estructura

```
ev08/device_systems/
├── app/
│   ├── main.py
│   ├── data/
│   │   └── users_db.py             # base de datos en memoria y siguiente_id()
│   ├── schemas/
│   │   └── user_schema.py          # + UserUpdate, UserPatch, MessageResponse
│   ├── routes/
│   │   └── user_routes.py          # + PUT, PATCH, DELETE
│   ├── services/
│   │   └── user_service.py         # logica de negocio (sin FastAPI)
│   └── dependencies/
│       └── user_dependencies.py    # funciones para Depends()
└── requirements.txt
```

**Por que las 5 capas:** el instructor pregunta seguro. Respuesta:

| Capa | Responsabilidad |
|---|---|
| `routes` | Traducir HTTP a llamadas a services. **No** contiene logica. |
| `schemas` | Contratos de entrada y salida validados por Pydantic. |
| `services` | Reglas de negocio. **No** conoce FastAPI. Se podria reusar en un CLI. |
| `dependencies` | Funciones para `Depends()`: buscar usuario, validar email, etc. |
| `data` | Simulacion de la BD. En EV09 se reemplaza por SQLAlchemy. |

### 2.2 Novedades en `schemas/user_schema.py`

- **`UserUpdate`** (linea 67): hereda de `UserBase`, es para **PUT** (reemplazo
  completo, todos los campos obligatorios).
- **`UserPatch`** (linea 82): **todos los campos son `Optional`**, para PATCH
  (actualizacion parcial). Tiene su propio validador de nombre.
- **`MessageResponse`** (linea 120): respuesta con solo `{"message": "..."}`,
  usada por DELETE.
- **`ErrorResponse`** (linea 126): formato estructurado de error usado en la
  documentacion (`error`, `message`, `status_code`).

**Por que PUT usa `UserUpdate` (obligatorio) y PATCH usa `UserPatch` (opcional):**
por semantica REST. PUT reemplaza el recurso completo; PATCH modifica
parcialmente. Si en PUT dejo `email` como opcional, se podria borrar por
descuido.

### 2.3 `services/user_service.py`

Funciones que **no importan FastAPI**. Solo trabajan con la lista en memoria.
Esta capa se puede probar sin levantar el servidor.

Funciones clave:

- `listar_usuarios(role, is_active)`: aplica los filtros.
- `obtener_por_id(user_id)`: `for/return None`.
- `email_duplicado(email, excluir_id=None)`: **truco importante**: en PATCH y PUT
  se pasa `excluir_id` para permitir que el mismo usuario mantenga su correo.
- `crear_usuario(datos)`: convierte el schema a dict y lo agrega a la lista.
- `actualizar_usuario(usuario, datos)`: **reemplaza todos los campos** (PUT).
- `actualizar_parcial(usuario, datos)`: usa `model_dump(exclude_unset=True,
  exclude_none=True)` para tomar solo lo que el cliente envio.
- `eliminar_usuario(usuario)`: `users_db.remove(usuario)`.

**Por que `exclude_unset=True` en PATCH:** distingue entre "el cliente no envio
el campo" y "el cliente envio `null`". Solo se actualizan los campos que
llegaron en el body.

### 2.4 `dependencies/user_dependencies.py` (LO QUE PIDE LA GUIA CON DEPENDS)

Cada funcion es una **dependencia** que se inyecta en las rutas con
`Depends()`. Sirven para no repetir logica.

- **`get_api_settings()`** (linea 15): devuelve la config general. Se usa en
  `GET /` con `config: Dict = Depends(get_api_settings)`.
- **`get_user_or_404(user_id)`** (linea 25): **la mas importante**. Busca el
  usuario y si no existe lanza 404. Se usa en GET/PUT/PATCH/DELETE por ID,
  y se **reutiliza** entre todos los endpoints. Este es el patron que la
  guia pide.
- **`validar_email_unico(usuario)`** (linea 43): usada en el POST para bloquear
  correos duplicados.
- **`validar_email_unico_en_actualizacion(datos, usuario_actual)`** (linea 53):
  usada en PUT. Recibe `usuario_actual` inyectado desde `get_user_or_404`
  (dependencias anidadas), para excluirlo de la comparacion.
- **`validar_patch_no_vacio(datos, usuario_actual)`** (linea 66): rechaza el
  PATCH sin datos con 400 y valida email si viene.
- **`validar_rol_permitido(role)`** (linea 90): valida el query parameter
  `role` y responde 400 en vez del 422 automatico.
- **`verificar_api_key(x_api_key)`** (linea 110): autenticacion simulada por
  cabecera `X-API-Key` (dependencia opcional, la guia lo sugiere).

**Por que separar dependencias:** una sola funcion (`get_user_or_404`) se usa
en 4 endpoints. Si se cambia la logica de busqueda, se cambia en un solo
lugar.

### 2.5 `routes/user_routes.py`

Cada endpoint recibe la dependencia y solo llama al service.

- `GET /users`: usa `Depends(validar_rol_permitido)` para el filtro `role`.
- `GET /users/{user_id}`: `Depends(get_user_or_404)` -> el usuario ya llega
  cargado.
- `POST /users`: `datos: UserCreate = Depends(validar_email_unico)`.
- `PUT /users/{user_id}`: recibe `Depends(get_user_or_404)` + `Depends(
  validar_email_unico_en_actualizacion)`.
- `PATCH /users/{user_id}`: `Depends(get_user_or_404)` + `Depends(
  validar_patch_no_vacio)`.
- `DELETE /users/{user_id}`: `Depends(get_user_or_404)`, elimina y devuelve
  200 con mensaje.

**Por que DELETE devuelve 200 y no 204:** la guia da dos opciones y aca se
eligio 200 OK con mensaje para dar feedback al cliente. En EV10 el DELETE
de dispositivos usa 204 No Content, para mostrar las dos formas.

### 2.6 `main.py` - manejo de errores

Tres manejadores de excepcion (linea 64 - 96):

- `@app.exception_handler(HTTPException)`: cualquier `HTTPException` se
  formatea como `{error: true, message, status_code, path}`.
- `@app.exception_handler(RequestValidationError)`: los errores 422 de
  Pydantic tambien se formatean con la lista de campos y mensajes.

**Por que respuestas estructuradas de error:** el consumidor (frontend, otro
servicio) siempre sabe donde leer el mensaje sin importar el codigo.

### 2.7 Codigos HTTP (tabla que hay que saber de memoria)

| Operacion | Metodo | Codigo |
|---|---|---|
| Listar | GET | 200 |
| Consultar por ID | GET | 200 |
| Crear | POST | 201 |
| Actualizar completo | PUT | 200 |
| Actualizar parcial | PATCH | 200 |
| Eliminar | DELETE | 200 (aca) / 204 No Content (EV10) |
| No encontrado | Cualquiera | 404 |
| Correo duplicado | POST/PUT | 400 |
| PATCH vacio | PATCH | 400 |
| Datos invalidos | Pydantic | 422 |

### 2.8 Preguntas tipicas EV08

- **"¿Como funciona Depends()?"** -> FastAPI ejecuta la funcion, guarda el
  resultado y lo pasa como parametro al endpoint. Sirve para no repetir
  codigo y para inyectar dependencias en pruebas.
- **"¿Donde controlas que el PATCH no venga vacio?"** -> dependencia
  `validar_patch_no_vacio` en `user_dependencies.py:66`.
- **"¿Por que separas services de routes?"** -> para que la logica sea
  reutilizable y no dependa de FastAPI. Se puede probar sin cliente HTTP.
- **"¿Que hace `model_dump(exclude_unset=True)`?"** -> devuelve solo los
  campos que el cliente **envio explicitamente**, ideal para PATCH.
- **"Diferencia entre 400 y 422"** -> 400 = la peticion es sintacticamente
  correcta pero incumple una regla de negocio (correo duplicado). 422 =
  el body no cumple con el schema Pydantic.
- **"¿Como devuelves un 404 si el usuario no existe?"** -> dependencia
  `get_user_or_404` en `user_dependencies.py:25`.

---

## 3. EV09 - Persistencia con SQLAlchemy (v3.0.0)

**Objetivo:** cambiar la lista en memoria por **base de datos SQLite** con
SQLAlchemy 2.x. Aparecen el engine, `SessionLocal`, `Base` y el modelo
`User` con constraints.

### 3.1 Estructura

```
ev09/device_systems/
├── app/
│   ├── main.py
│   ├── database/
│   │   └── connection.py           # engine, SessionLocal, Base, crear_tablas
│   ├── models/
│   │   └── user_model.py           # tabla users (SQLAlchemy)
│   ├── schemas/
│   │   └── user_schema.py          # + created_at, from_attributes=True
│   ├── routes/
│   │   └── user_routes.py          # usa Depends(get_db)
│   ├── services/
│   │   └── user_service.py         # ahora usa Session
│   └── dependencies/
│       └── database_dependency.py  # get_db() y get_user_or_404 con BD
├── seed.py                         # datos de ejemplo
├── requirements.txt
└── device_systems.db               # SQLite generado
```

### 3.2 `database/connection.py` (aca vive la conexion)

```python
DATABASE_URL = "sqlite:///./device_systems.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    """Base declarativa de los modelos SQLAlchemy."""
```

**Por que `check_same_thread=False`:** SQLite por defecto solo permite usar
la conexion en el hilo que la abrio; FastAPI corre endpoints en varios
hilos, entonces hay que desactivar esa comprobacion. Con Postgres o MySQL
no haria falta.

**Por que `autoflush=False, autocommit=False`:** para controlar
explicitamente cuando se manda el commit. Evita que un simple `select`
guarde cambios sin querer.

**`crear_tablas()`**: llama a `Base.metadata.create_all(bind=engine)`. Se
invoca desde el `lifespan` de la app (`main.py:33`) para que las tablas
existan al arrancar.

### 3.3 `models/user_model.py` (modelo de la tabla)

```python
class User(Base):
    __tablename__ = "users"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    name:       Mapped[str]      = mapped_column(String(60), nullable=False)
    email:      Mapped[str]      = mapped_column(String(120), unique=True, nullable=False, index=True)
    role:       Mapped[str]      = mapped_column(String(20), nullable=False)
    is_active:  Mapped[bool]     = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora, nullable=False)
```

**Constraints (lo que pregunta la guia):**

- `primary_key=True` en `id`.
- `unique=True` en `email` -> a nivel base de datos, evita duplicados
  aunque falle la validacion Pydantic.
- `nullable=False` en `name`, `email`, `role`, `is_active`.
- `index=True` en `id`, `email` -> acelera busquedas.
- `default=True` en `is_active`, `default=ahora` en `created_at` (funcion
  que devuelve `datetime.now(timezone.utc)`).

### 3.4 `schemas/user_schema.py` (diferencia clave con EV08)

- `UserResponse` incluye `created_at: datetime`.
- `model_config = ConfigDict(from_attributes=True)` -> **permite construir
  un schema Pydantic a partir de un objeto SQLAlchemy** con
  `UserResponse.model_validate(usuario)`.
- Se agrega `OrdenUsuarios` (`Enum`) con `NAME` y `CREATED_AT` para el
  parametro `order_by`.

**"¿Cual es la diferencia entre modelo y schema?"** (respuesta lista):

| Modelo SQLAlchemy | Schema Pydantic |
|---|---|
| Representa la **tabla** de la BD | Representa el **contrato HTTP** |
| Columnas, tipos SQL, constraints | Campos, tipos Python, validaciones |
| Lo valida el motor de BD | Lo valida Pydantic **antes** de tocar la BD |
| Ejemplo: `unique=True` | Ejemplo: `EmailStr` |
| Error: `IntegrityError` -> 400 | Error: 422 |

### 3.5 `dependencies/database_dependency.py`

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Por que `yield` y no `return`:** despues del `yield`, FastAPI ejecuta el
resto del bloque (`db.close()`) **incluso si la ruta lanza excepcion**.
Es el patron oficial para manejo de recursos en FastAPI.

`get_user_or_404` ahora recibe la sesion tambien inyectada:

```python
def get_user_or_404(user_id: int = Path(...), db: Session = Depends(get_db)) -> User:
    ...
```

### 3.6 `services/user_service.py` (aca vive el CRUD de verdad)

Todas las funciones reciben `db: Session` como primer parametro.

- `listar_usuarios(db, role, is_active, order_by, descendente)`:
  ```python
  consulta = select(User)
  if role is not None:
      consulta = consulta.where(User.role == role.value)
  if is_active is not None:
      consulta = consulta.where(User.is_active == is_active)
  consulta = consulta.order_by(asc/desc(columna))
  return list(db.execute(consulta).scalars().all())
  ```
- `obtener_por_id(db, user_id)`: `db.get(User, user_id)` (busca por PK, es
  el metodo mas rapido).
- `obtener_por_email(db, email)`: `select(...).where(User.email == email)`.
- `crear_usuario(db, datos)`:
  ```python
  usuario = User(...)
  db.add(usuario); db.commit(); db.refresh(usuario)
  return usuario
  ```
- `actualizar_usuario` / `actualizar_parcial`: modifican atributos del
  objeto, `db.commit()` y `db.refresh()`.
- `eliminar_usuario`: `db.delete(usuario)` + `db.commit()`.

**Por que `db.refresh(usuario)` despues de commit:** para recargar los
campos generados por la BD (`id`, `created_at`) en el objeto Python.

### 3.7 `main.py` novedades EV09

- **`lifespan`** (linea 33): crea las tablas al iniciar la aplicacion.
- **`@app.exception_handler(IntegrityError)`** (linea 103): traduce las
  violaciones de constraints de SQLAlchemy (como `unique` roto por una
  race condition) a 400 Bad Request en vez de un 500 feo.

### 3.8 Preguntas tipicas EV09

- **"¿Como conectas FastAPI con la BD?"** -> `create_engine` en
  `connection.py:14`, `sessionmaker` en la linea 20, dependencia `get_db()`
  en `database_dependency.py:13`.
- **"¿Que es la Base declarativa?"** -> clase que hereda `DeclarativeBase`;
  todos los modelos heredan de ella y SQLAlchemy registra sus tablas en
  `Base.metadata`.
- **"¿Que hace `Base.metadata.create_all()`?"** -> genera las tablas en la
  BD a partir de los modelos registrados.
- **"¿Diferencia entre modelo y schema?"** -> ver tabla en la seccion 3.4.
- **"¿Como manejas el 400 cuando el correo esta duplicado?"** -> primero,
  `email_duplicado` en el service; segundo, respaldo con
  `IntegrityError` handler en `main.py:103` por si dos peticiones
  simultaneas pasan la validacion.
- **"¿Que hace `from_attributes=True`?"** -> permite que un `UserResponse`
  se construya a partir de un objeto `User` de SQLAlchemy, sin
  convertirlo a dict manualmente.
- **"¿Como haces query con filtros y orden?"** -> se muestra
  `listar_usuarios` en `user_service.py:22` con `select(User).where(
  ...).order_by(...)`.
- **"¿Por que usas `yield` en get_db?"** -> para cerrar la sesion en el
  `finally`, aunque la ruta lance excepcion.

---

## 4. EV10 - Alembic, relaciones y consultas con joins (v4.0.0)

**Objetivo:** migraciones controladas con Alembic, agregar los modelos
`Device` y `Loan`, relaciones one-to-many (User-Loan y Device-Loan) y
consultas con joins y filtros avanzados.

### 4.1 Estructura

```
ev10/device_systems/
├── app/
│   ├── main.py
│   ├── database/connection.py
│   ├── models/
│   │   ├── user_model.py       # + loans (relationship)
│   │   ├── device_model.py     # nuevo
│   │   └── loan_model.py       # nuevo (FK a users y devices)
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py
│   ├── routes/
│   │   ├── user_routes.py      # + /users/{id}/loans
│   │   ├── device_routes.py    # nuevo
│   │   └── loan_routes.py      # nuevo
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py   # nuevo
│   │   └── loan_service.py     # nuevo, con joins
│   └── dependencies/database_dependency.py  # + get_device_or_404, get_loan_or_404
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 75b8b80c779a_create_users_table.py
│       └── e61a53a3b60c_create_devices_and_loans_tables.py
├── alembic.ini
├── seed.py
├── requirements.txt
└── device_systems.db
```

### 4.2 Alembic (el bloque que pide la guia)

**Que es Alembic:** herramienta oficial de migraciones para SQLAlchemy.
Cada cambio en las tablas se guarda como un archivo Python con `upgrade()`
y `downgrade()`.

**Comandos que hay que ejecutar en la demo:**

```bash
alembic init alembic                                  # (ya hecho, no repetir)
alembic revision --autogenerate -m "create devices and loans tables"
alembic upgrade head
alembic history
alembic current
alembic downgrade -1     # opcional, deshace la ultima migracion
```

**`alembic.ini` (raiz del proyecto):**

- `script_location = %(here)s/alembic` -> dice donde estan los scripts.
- `sqlalchemy.url` esta comentado porque en `env.py` se sobreescribe con
  el `DATABASE_URL` del proyecto.

**`alembic/env.py`** (la unica personalizacion importante, lineas 22 - 34):

```python
sys.path.append(...)                               # para importar `app`
from app.database.connection import DATABASE_URL, Base
import app.models                                  # registra User, Device, Loan

config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata
```

**Por que se hace esto:** `target_metadata = Base.metadata` es lo que
Alembic compara contra la BD real para autogenerar cada migracion.

**Los dos archivos de migracion (`alembic/versions/`):**

- `75b8b80c779a_create_users_table.py`: crea la tabla `users` con sus
  columnas y el indice sobre `email`.
- `e61a53a3b60c_create_devices_and_loans_tables.py`: crea `devices` y
  `loans`, con las **foreign keys** de `loans` hacia `users.id` y
  `devices.id`.

**"¿Por que Alembic y no `Base.metadata.create_all()`?"** ->
`create_all` sirve para desarrollo, pero en produccion cada cambio de
schema debe ser rastreable, reversible y aplicable en orden. Alembic da
control de versiones para la BD.

### 4.3 Modelos (`app/models/`)

**`user_model.py` (linea 37):** ahora tiene la relacion:

```python
loans: Mapped[List["Loan"]] = relationship(
    "Loan", back_populates="user", cascade="all, delete-orphan",
)
```

**`device_model.py`:** tabla `devices` con `serial_number` unico e indexado.
Tambien tiene `loans: relationship(back_populates="device", cascade=...)`.

**`loan_model.py`:** tabla `loans`. Aca estan las claves foraneas:

```python
user_id:   Mapped[int] = mapped_column(Integer, ForeignKey("users.id",   ondelete="CASCADE"), nullable=False, index=True)
device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
```

Y las relaciones Many-to-One:

```python
user:   Mapped[User]   = relationship("User",   back_populates="loans")
device: Mapped[Device] = relationship("Device", back_populates="loans")
```

**"¿Que es `back_populates`?"** -> le dice a SQLAlchemy que las dos
relaciones (User.loans y Loan.user) son la misma en direcciones opuestas.
Si agrego un `Loan` a `user.loans`, `loan.user` queda apuntando a ese
usuario automaticamente.

**"¿Que es `cascade='all, delete-orphan'`?"** -> si elimino un `User`,
sus `Loan` asociados tambien se eliminan (integridad referencial).

**"¿Que es `ondelete='CASCADE'` en la ForeignKey?"** -> el mismo cascade
pero a nivel de base de datos (por si alguien borra desde SQL puro).

### 4.4 Consultas con joins (`app/services/loan_service.py`)

**`_consulta_con_relaciones()`** (linea 22):

```python
return select(Loan).options(joinedload(Loan.user), joinedload(Loan.device))
```

**Por que `joinedload`:** carga el usuario y el dispositivo en la **misma**
consulta SQL (LEFT OUTER JOIN), evitando el problema **N+1** (una query
por prestamo para traer su usuario y su dispositivo).

**`listar_prestamos(...)`** (linea 28) usa las funciones que la guia
menciona:

- `select`, `where`, `join`, `and_`, `ilike`.

Estructura:

```python
consulta = _consulta_con_relaciones()
condiciones = []

if status:      condiciones.append(Loan.status == status.value)
if user_id:     condiciones.append(Loan.user_id == user_id)
if device_id:   condiciones.append(Loan.device_id == device_id)

if user_email:
    consulta = consulta.join(User, Loan.user_id == User.id)
    condiciones.append(User.email.ilike(f"%{user_email}%"))

if device_type or search:
    consulta = consulta.join(Device, Loan.device_id == Device.id)
    if device_type: condiciones.append(Device.device_type == device_type.value)
    if search:      condiciones.append(Device.name.ilike(f"%{search}%"))

if condiciones:
    consulta = consulta.where(and_(*condiciones))

consulta = consulta.order_by(Loan.loan_date.desc())
return list(db.execute(consulta).unique().scalars().all())
```

**Por que `.unique()`:** cuando se usa `joinedload`, un `scalars().all()`
puede devolver el mismo prestamo repetido; `.unique()` lo evita.

**Endpoints de consulta con joins:**

- `GET /loans` -> lista con filtros.
- `GET /loans/details` -> mismo listado pero devuelve el schema
  `LoanDetailResponse` con datos del usuario y del dispositivo.
- `GET /loans/{loan_id}` -> un prestamo con relaciones.
- `GET /users/{user_id}/loans` -> **join hacia users**, lista los
  prestamos del usuario.
- `GET /devices/{device_id}/loans` -> historial del dispositivo.

### 4.5 Reglas de negocio del prestamo (`POST /loans`)

En `loan_routes.py:142`:

1. Verifica que el usuario exista (`user_service.obtener_por_id`).
   Si no, 404.
2. Verifica que el dispositivo exista. Si no, 404.
3. Verifica `dispositivo.is_available == True`. Si no, **409 Conflict**
   ("El dispositivo no esta disponible").
4. Si todo bien, `loan_service.crear_prestamo`:
   - Inserta `Loan` con `status = "active"`.
   - Cambia `dispositivo.is_available = False`.
   - Hace commit atomico de las dos operaciones.

**Por que 409 y no 400:** 409 Conflict describe mejor "el recurso existe
pero su estado no permite la operacion". 400 Bad Request seria si la
peticion en si estuviera mal formada.

### 4.6 Devolucion del prestamo (`PATCH /loans/{loan_id}/return`)

En `loan_routes.py:185`:

1. `Depends(get_loan_or_404)` carga el prestamo o 404.
2. Si `status == "returned"` -> 409 Conflict ("El prestamo ya fue devuelto").
3. Sino, `loan_service.devolver_prestamo`:
   - `status = "returned"`, `return_date = ahora()`.
   - `prestamo.device.is_available = True` (**se accede a la relacion, no
     hace falta consultar el dispositivo**).
   - Commit.

**Por que aca aprovechamos `back_populates`:** `prestamo.device` es el
objeto Device gracias a la relacion; se modifica y en el mismo commit
se guarda todo.

### 4.7 CRUD de dispositivos (`app/routes/device_routes.py`)

Endpoints principales:

- `GET /devices` con filtros: `device_type`, `is_available`, `brand`,
  `search` (ilike sobre name/serial/brand).
- `GET /devices/{device_id}`.
- `GET /devices/{device_id}/loans` (join con loans).
- `POST /devices` -> 201, `serial_number` unico.
- `PUT`, `PATCH`, `DELETE`.
- **`DELETE`** responde 204 No Content, y si el dispositivo esta prestado
  (`is_available == False`) responde **409 Conflict** ("No se puede
  eliminar un dispositivo que esta prestado").

### 4.8 Codigos HTTP EV10 (tabla completa)

| Caso | Codigo |
|---|---|
| Registro creado | 201 |
| Consulta exitosa | 200 |
| Devolucion exitosa | 200 |
| Eliminacion exitosa | 204 |
| Recurso no encontrado | 404 |
| Dato duplicado (email, serial) | 400 |
| Regla de negocio incumplida (no disponible, ya devuelto) | 409 |
| Validacion Pydantic | 422 |

### 4.9 Preguntas tipicas EV10

- **"Muestrame donde configuras Alembic"** -> `alembic.ini` (raiz) y
  `alembic/env.py` (lineas 22 - 34, `target_metadata = Base.metadata`).
- **"¿Como generas una migracion?"** ->
  `alembic revision --autogenerate -m "..."`. Detecta cambios entre los
  modelos y la BD.
- **"¿Que hace `alembic upgrade head`?"** -> aplica todas las migraciones
  pendientes hasta la ultima. `alembic downgrade -1` deshace la ultima.
- **"Muestrame la relacion entre User y Loan"** -> `user_model.py:37`
  (`loans = relationship(...)`) y `loan_model.py:46` (`user = relationship
  ("User", back_populates="loans")`).
- **"¿Que es `back_populates`?"** -> ver 4.3.
- **"¿Como haces un join?"** -> `loan_service.py:55` -> `.join(User,
  Loan.user_id == User.id)` y despues `.where(User.email.ilike(...))`.
- **"¿Que evita el problema N+1?"** -> `joinedload(Loan.user)`; trae
  usuario y dispositivo en la misma consulta.
- **"¿Como validas que el dispositivo esta disponible al prestar?"** ->
  `loan_routes.py:161` -> `if not dispositivo.is_available: raise 409`.
- **"¿Que pasa si borro un usuario?"** -> por `cascade="all,
  delete-orphan"` y `ondelete="CASCADE"`, sus prestamos se borran
  automaticamente.
- **"¿Como buscas por email parcial?"** -> `User.email.ilike(f"%{email}%")`
  en `loan_service.py:56`.
- **"¿Cual es la diferencia entre `like` y `ilike`?"** -> `ilike` es
  insensible a mayusculas.
- **"¿Por que 409 en vez de 400?"** -> 409 = conflicto con el estado
  actual del recurso.

---

## 5. Reflexion final para la socializacion (5 minutos)

Guion posible:

1. **Que hice** (30s): implemente device_systems, una API REST que
   evoluciono desde GET/POST simples hasta un CRUD con base de datos,
   migraciones y consultas con joins.
2. **Como esta organizado** (1 min): separacion por capas (routes,
   schemas, services, dependencies, models, database). Cada capa tiene
   una responsabilidad clara; eso hace el codigo mas facil de mantener.
3. **Que aprendi de FastAPI** (1 min):
   - Pydantic v2 valida solo, con `EmailStr`, `Enum`, `Field`.
   - `Depends()` permite reutilizar logica y hacer inyeccion.
   - Swagger/ReDoc se generan solos y sirven de herramienta de prueba.
4. **Como uso SQLAlchemy y Alembic** (1.5 min):
   - `Base` + modelos declarativos con `Mapped[]`.
   - Sesion inyectada con `get_db()`.
   - Constraints (`unique`, `nullable`, `ForeignKey`).
   - Migraciones versionadas con Alembic.
5. **Que aprendi de modelado relacional** (1 min):
   - Relacion one-to-many con `relationship` + `back_populates`.
   - Integridad referencial con `ForeignKey` + `cascade`.
   - Consultas eficientes con `joinedload` (evita N+1).
6. **Cierre** (30s): la API pasa de ser un ejemplo en memoria a un
   servicio con persistencia, control de estado y consultas relacionales,
   listo para desplegarse.

---

## 6. Comandos de emergencia durante la demo

Si algo falla en vivo:

```bash
# EV07/EV08: reset simple
uvicorn app.main:app --reload

# EV09: si la BD se corrompe
rm device_systems.db
python seed.py                    # opcional (crea 3 usuarios de ejemplo)
uvicorn app.main:app --reload

# EV10: si Alembic se pierde
rm device_systems.db
alembic upgrade head
python seed.py                    # crea usuarios y dispositivos
uvicorn app.main:app --reload

# Probar un endpoint sin Swagger
curl http://127.0.0.1:8000/users
curl -X POST http://127.0.0.1:8000/users \
     -H "Content-Type: application/json" \
     -d "{\"name\":\"Ana Perez\",\"email\":\"ana@sena.edu.co\",\"role\":\"admin\",\"is_active\":true}"
```

---

## 7. Chuleta ultra-corta (para memorizar el dia antes)

- **FastAPI**: framework asincrono en Python; genera Swagger solo.
- **Pydantic**: validacion; `Field`, `EmailStr`, `Enum`, `field_validator`.
- **Path parameter**: `/users/{user_id}`; declarar `Path(..., ge=1)`.
- **Query parameter**: `?role=admin`; declarar `Query(default=None)`.
- **Response Model**: schema Pydantic en el decorador
  `@router.get(..., response_model=UserResponse)`.
- **Cabeceras**: se agregan con `response.headers[...] = ...` o middleware.
- **Depends()**: inyecta dependencias; sirve para reusar `get_db`,
  `get_user_or_404`, etc.
- **HTTPException**: para errores controlados (`raise HTTPException(404,
  "detalle")`).
- **SQLAlchemy 2.x**: `select`, `where`, `order_by`, `join`; sesion con
  `Session`.
- **`db.commit()` + `db.refresh(obj)`**: guarda y recarga el objeto.
- **Alembic**: `init`, `revision --autogenerate`, `upgrade head`,
  `history`, `downgrade -1`.
- **ForeignKey + relationship + back_populates**: relaciones entre
  tablas.
- **Codigos HTTP**: 200 (OK), 201 (Created), 204 (No Content), 400 (Bad
  Request), 404 (Not Found), 409 (Conflict), 422 (Unprocessable Entity).
