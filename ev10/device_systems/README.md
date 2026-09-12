# device_systems — Alembic, Relaciones y Joins (EV10)

**Evidencia:** [Proyecto-Final-v1] GA1-220501096-01-AA1-EV10 — FastAPI Avanzado
**Aprendiz:** Daniel Roman
**Version de la API:** 4.0.0
**Rama de trabajo:** `device_systems_alembic_relaciones` (unificada con `main`)

---

## 1. Descripcion de la API

`device_systems` pasa de ser un CRUD de una sola tabla a un **sistema relacional**
que gestiona **usuarios**, **dispositivos** y **prestamos**:

- Migraciones de base de datos versionadas con **Alembic**.
- Tres modelos relacionados: `User` **1-N** `Loan` **N-1** `Device`.
- Integridad referencial con `ForeignKey()` y navegacion con `relationship()`.
- Consultas con **joins** que devuelven informacion combinada de las tres tablas.
- Filtros avanzados con `where()`, `ilike()`, `and_()` y `or_()`.
- Reglas de negocio del prestamo y la devolucion de dispositivos.

## 2. Tecnologias utilizadas

| Tecnologia | Uso |
|---|---|
| FastAPI | Framework de la API REST |
| SQLAlchemy 2.x | ORM, relaciones y consultas |
| Alembic | Migraciones de base de datos |
| SQLite | Motor de base de datos |
| Pydantic v2 | Schemas de entrada y salida |
| Uvicorn | Servidor ASGI |

## 3. Estructura del proyecto

```
device_systems/
│── app/
│   │── main.py
│   │
│   │── database/
│   │   │── connection.py
│   │
│   │── models/
│   │   │── user_model.py          # User + relationship loans
│   │   │── device_model.py        # Device + relationship loans
│   │   │── loan_model.py          # Loan + ForeignKey a users y devices
│   │
│   │── schemas/
│   │   │── user_schema.py
│   │   │── device_schema.py
│   │   │── loan_schema.py         # incluye LoanDetailResponse (join)
│   │
│   │── routes/
│   │   │── user_routes.py
│   │   │── device_routes.py
│   │   │── loan_routes.py
│   │
│   │── services/
│   │   │── user_service.py
│   │   │── device_service.py
│   │   │── loan_service.py        # consultas con joins y filtros
│   │
│   │── dependencies/
│   │   │── database_dependency.py # get_db, get_user_or_404, get_device_or_404, get_loan_or_404
│
│── alembic/
│   │── env.py                     # configurado con Base.metadata del proyecto
│   │── versions/
│   │   │── 75b8b80c779a_create_users_table.py
│   │   │── e61a53a3b60c_create_devices_and_loans_tables.py
│
│── alembic.ini
│── capturas/
│── seed.py
│── requirements.txt
│── README.md
```

## 4. Instalacion y ejecucion

```bash
cd ev10/device_systems
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

| Recurso | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

## 5. Alembic — configuracion y migraciones

### 5.1 Instalacion e inicializacion

```bash
pip install alembic
alembic init alembic
```

### 5.2 Configuracion

En `alembic.ini`:

```ini
sqlalchemy.url = sqlite:///./device_systems.db
```

En `alembic/env.py` se agrego la raiz del proyecto al `sys.path`, se importan los
modelos y se define la metadata objetivo:

```python
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import DATABASE_URL, Base
import app.models  # registra User, Device y Loan

config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata
```

También se activó `render_as_batch=True`, necesario para que SQLite pueda aplicar
cambios de estructura (`ALTER TABLE` limitado).

### 5.3 Migraciones generadas

```bash
alembic revision --autogenerate -m "create users table"
alembic revision --autogenerate -m "create devices and loans tables"
alembic upgrade head
```

Historial real del proyecto:

```
$ alembic history
75b8b80c779a -> e61a53a3b60c (head), create devices and loans tables
<base> -> 75b8b80c779a, create users table

$ alembic current
e61a53a3b60c (head)
```

| Revision | Descripcion | Tablas afectadas |
|---|---|---|
| `75b8b80c779a` | `create users table` | `users` |
| `e61a53a3b60c` | `create devices and loans tables` | `devices`, `loans` |

Comandos utiles:

| Comando | Que hace |
|---|---|
| `alembic revision --autogenerate -m "mensaje"` | Compara modelos vs base y genera la migracion |
| `alembic upgrade head` | Aplica todas las migraciones pendientes |
| `alembic downgrade -1` | Revierte la ultima migracion |
| `alembic history` | Muestra el historial de migraciones |
| `alembic current` | Muestra la revision aplicada actualmente |

## 6. Modelos y asociaciones

### 6.1 Tabla `devices`

| Campo | Tipo | Restriccion |
|---|---|---|
| `id` | Integer | Primary Key |
| `name` | String(80) | Obligatorio |
| `serial_number` | String(50) | Unico y obligatorio |
| `device_type` | String(30) | Obligatorio (laptop, tablet, proyector, camara, router, monitor) |
| `brand` | String(40) | Opcional |
| `is_available` | Boolean | Por defecto `True` |
| `created_at` | DateTime | Fecha de creacion |

### 6.2 Tabla `loans`

| Campo | Tipo | Restriccion |
|---|---|---|
| `id` | Integer | Primary Key |
| `user_id` | Integer | `ForeignKey("users.id")` |
| `device_id` | Integer | `ForeignKey("devices.id")` |
| `loan_date` | DateTime | Fecha del prestamo |
| `return_date` | DateTime | Opcional |
| `status` | String(20) | `active`, `returned`, `overdue` |

### 6.3 Relaciones

```python
# app/models/user_model.py
loans: Mapped[List["Loan"]] = relationship("Loan", back_populates="user")

# app/models/device_model.py
loans: Mapped[List["Loan"]] = relationship("Loan", back_populates="device")

# app/models/loan_model.py
user: Mapped[User] = relationship("User", back_populates="loans")
device: Mapped[Device] = relationship("Device", back_populates="loans")
```

```
users (1) ──────< loans >────── (1) devices
        un usuario           un dispositivo
        muchos prestamos     muchos prestamos historicos
```

## 7. Tabla de endpoints

### Users

| Metodo | Endpoint | Descripcion | Codigo |
|---|---|---|---|
| `GET` | `/users` | Lista usuarios (filtros `role`, `is_active`, orden) | `200` |
| `GET` | `/users/{user_id}` | Consulta un usuario | `200` / `404` |
| `GET` | `/users/{user_id}/loans` | **Join**: prestamos del usuario | `200` / `404` |
| `POST` | `/users` | Crea un usuario | `201` / `400` |
| `PUT` | `/users/{user_id}` | Actualiza completo | `200` / `404` |
| `PATCH` | `/users/{user_id}` | Actualiza parcial | `200` / `400` / `404` |
| `DELETE` | `/users/{user_id}` | Elimina | `200` / `404` |

### Devices

| Metodo | Endpoint | Descripcion | Codigo |
|---|---|---|---|
| `GET` | `/devices` | Lista dispositivos | `200` |
| `GET` | `/devices?device_type=laptop` | Filtra por tipo | `200` |
| `GET` | `/devices?is_available=true` | Filtra por disponibilidad | `200` |
| `GET` | `/devices?brand=lenovo` | Filtra por marca (`ilike`) | `200` |
| `GET` | `/devices?search=thinkpad` | Busca en nombre, serial y marca (`or_` + `ilike`) | `200` |
| `GET` | `/devices/{device_id}` | Consulta un dispositivo | `200` / `404` |
| `GET` | `/devices/{device_id}/loans` | **Join**: historial del dispositivo | `200` / `404` |
| `POST` | `/devices` | Registra un dispositivo | `201` / `400` |
| `PUT` | `/devices/{device_id}` | Actualiza completo | `200` / `404` |
| `PATCH` | `/devices/{device_id}` | Actualiza parcial | `200` / `400` / `404` |
| `DELETE` | `/devices/{device_id}` | Elimina (si no esta prestado) | `200` / `409` / `404` |

### Loans

| Metodo | Endpoint | Descripcion | Codigo |
|---|---|---|---|
| `GET` | `/loans` | Lista prestamos con filtros | `200` |
| `GET` | `/loans/details` | **Join**: prestamos con usuario y dispositivo | `200` |
| `GET` | `/loans/{loan_id}` | Consulta un prestamo con su detalle | `200` / `404` |
| `POST` | `/loans` | Registra un prestamo | `201` / `404` / `409` |
| `PATCH` | `/loans/{loan_id}/return` | Registra la devolucion | `200` / `404` / `409` |
| `PATCH` | `/loans/{loan_id}` | Cambia el estado del prestamo | `200` / `404` |

Filtros de `/loans` y `/loans/details`: `status`, `user_id`, `device_id`,
`user_email`, `device_type`, `search`.

## 8. Reglas de negocio del prestamo

**POST /loans**

1. Valida que el usuario exista → si no, `404`.
2. Valida que el dispositivo exista → si no, `404`.
3. Valida que el dispositivo este disponible → si no, `409 Conflict`.
4. Crea el prestamo con `status = "active"`.
5. Cambia `is_available` del dispositivo a `false`.

**PATCH /loans/{loan_id}/return**

1. Valida que el prestamo exista → si no, `404`.
2. Si ya estaba `returned` → `409 Conflict`.
3. Marca el prestamo como `returned` y asigna `return_date`.
4. Cambia `is_available` del dispositivo a `true`.

## 9. Consultas con joins y filtros

`app/services/loan_service.py` construye la consulta base trayendo las relaciones:

```python
def _consulta_con_relaciones():
    return select(Loan).options(joinedload(Loan.user), joinedload(Loan.device))
```

Y arma los filtros dinamicamente, usando `join()` solo cuando hace falta:

```python
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
```

En `device_service.py` la busqueda libre usa `or_()` sobre tres columnas:

```python
consulta = consulta.where(
    or_(
        Device.name.ilike(patron),
        Device.serial_number.ilike(patron),
        Device.brand.ilike(patron),
    )
)
```

## 10. Codigos de estado HTTP

| Caso | Codigo |
|---|---|
| Registro creado | `201 Created` |
| Consulta exitosa | `200 OK` |
| Devolucion exitosa | `200 OK` |
| Eliminacion exitosa | `200 OK` (con mensaje) |
| Recurso no encontrado | `404 Not Found` |
| Dato duplicado (email / serial) | `400 Bad Request` |
| Regla de negocio incumplida | `409 Conflict` |
| Error de validacion | `422 Unprocessable Entity` |

Errores controlados: usuario inexistente, dispositivo inexistente, dispositivo no
disponible, prestamo inexistente, devolver un prestamo ya devuelto, numero de serie
duplicado, correo duplicado, filtros invalidos y eliminacion de un dispositivo prestado.

## 11. Ejemplos de peticiones y respuestas

### 11.1 POST /devices

```bash
curl -X POST http://127.0.0.1:8000/devices -H "Content-Type: application/json" -d "{\"name\":\"Monitor LG 24\",\"serial_number\":\"lg-2024-030\",\"device_type\":\"monitor\",\"brand\":\"LG\"}"
```

```json
HTTP 201 Created
{
  "id": 5,
  "name": "Monitor LG 24",
  "serial_number": "LG-2024-030",
  "device_type": "monitor",
  "brand": "LG",
  "is_available": true,
  "created_at": "2026-09-12T17:34:38.329530"
}
```

### 11.2 POST /loans

Cuerpo: `{ "user_id": 1, "device_id": 1 }`

```json
HTTP 201 Created
{
  "loan_id": 1,
  "status": "active",
  "loan_date": "2026-09-12T17:34:38.520397",
  "return_date": null,
  "user":   { "id": 1, "name": "Ana Perez", "email": "ana@sena.edu.co" },
  "device": { "id": 1, "name": "Laptop Lenovo ThinkPad", "serial_number": "LEN-2024-001", "device_type": "laptop" }
}
```

Tras el prestamo, `GET /devices/1` devuelve `"is_available": false`.

### 11.3 POST /loans — dispositivo no disponible

```json
HTTP 409
{ "error": true, "message": "El dispositivo no esta disponible", "status_code": 409, "path": "/loans" }
```

### 11.4 GET /loans/details — consulta con joins

```json
HTTP 200
{
  "total": 2,
  "data": [
    {
      "loan_id": 2,
      "status": "active",
      "loan_date": "2026-09-12T17:34:38.681221",
      "return_date": null,
      "user":   { "id": 2, "name": "Carlos Gomez", "email": "carlos@sena.edu.co" },
      "device": { "id": 3, "name": "Proyector Epson PowerLite", "serial_number": "EPS-2023-007", "device_type": "proyector" }
    },
    {
      "loan_id": 1,
      "status": "active",
      "loan_date": "2026-09-12T17:34:38.520397",
      "return_date": null,
      "user":   { "id": 1, "name": "Ana Perez", "email": "ana@sena.edu.co" },
      "device": { "id": 1, "name": "Laptop Lenovo ThinkPad", "serial_number": "LEN-2024-001", "device_type": "laptop" }
    }
  ]
}
```

### 11.5 Filtros aplicados

```bash
curl "http://127.0.0.1:8000/loans?status=active"
curl "http://127.0.0.1:8000/loans/details?device_type=proyector"
curl "http://127.0.0.1:8000/loans/details?user_email=ana@sena.edu.co"
curl "http://127.0.0.1:8000/devices?search=thinkpad"
curl "http://127.0.0.1:8000/devices?brand=lenovo"
```

### 11.6 PATCH /loans/1/return — devolucion

```json
HTTP 200
{
  "loan_id": 1,
  "status": "returned",
  "loan_date": "2026-09-12T17:34:38.520397",
  "return_date": "2026-09-12T17:34:38.932840",
  "user":   { "id": 1, "name": "Ana Perez", "email": "ana@sena.edu.co" },
  "device": { "id": 1, "name": "Laptop Lenovo ThinkPad", "serial_number": "LEN-2024-001", "device_type": "laptop" }
}
```

Al consultar `GET /devices/1` el dispositivo vuelve a estar disponible:
`"is_available": true`.

### 11.7 Segunda devolucion del mismo prestamo

```json
HTTP 409
{ "error": true, "message": "El prestamo ya fue devuelto", "status_code": 409, "path": "/loans/1/return" }
```

### 11.8 GET /devices/1/loans — historial del dispositivo

```json
HTTP 200
{ "total": 1, "data": [ { "loan_id": 1, "status": "returned", "user": { "...": "..." }, "device": { "...": "..." } } ] }
```

## 12. Pruebas funcionales realizadas

| # | Prueba | Esperado | Resultado |
|---|---|---|---|
| 1 | Ejecutar migraciones con Alembic | 2 revisiones aplicadas | OK |
| 2 | Crear usuario | `201` | OK |
| 3 | Crear dispositivo | `201` | OK |
| 4 | Crear dispositivo con serial repetido | `400` | OK |
| 5 | Crear prestamo | `201` + dispositivo no disponible | OK |
| 6 | Prestar un dispositivo no disponible | `409` | OK |
| 7 | Prestar con usuario inexistente | `404` | OK |
| 8 | Prestar con dispositivo inexistente | `404` | OK |
| 9 | Listar prestamos con informacion relacionada | `200` con `user` y `device` | OK |
| 10 | Filtrar prestamos por estado | `200` | OK |
| 11 | Filtrar prestamos por tipo de dispositivo | `200` | OK |
| 12 | Filtrar prestamos por correo de usuario | `200` | OK |
| 13 | Consultar prestamos de un usuario | `200` | OK |
| 14 | Devolver un dispositivo | `200` + `status: returned` | OK |
| 15 | Validar que el dispositivo vuelva a estar disponible | `is_available: true` | OK |
| 16 | Devolver dos veces el mismo prestamo | `409` | OK |
| 17 | Consultar historial del dispositivo | `200` | OK |
| 18 | Eliminar un dispositivo prestado | `409` | OK |
| 19 | Consultar prestamo inexistente | `404` | OK |

## 13. Capturas

> Guarda las imagenes en `capturas/` con estos nombres.

| Evidencia | Captura |
|---|---|
| `alembic init alembic` | ![init](capturas/01-alembic-init.png) |
| `alembic revision --autogenerate` | ![revision](capturas/02-alembic-revision.png) |
| `alembic upgrade head` | ![upgrade](capturas/03-alembic-upgrade.png) |
| `alembic history` | ![history](capturas/04-alembic-history.png) |
| Tablas generadas (`users`, `devices`, `loans`) | ![tablas](capturas/05-tablas-generadas.png) |
| Swagger UI con los 3 tags | ![swagger](capturas/06-swagger-ui.png) |
| Crear usuario | ![usuario](capturas/07-crear-usuario.png) |
| Crear dispositivo | ![dispositivo](capturas/08-crear-dispositivo.png) |
| Crear prestamo | ![prestamo](capturas/09-crear-prestamo.png) |
| Prestamo de dispositivo no disponible (409) | ![409](capturas/10-prestamo-no-disponible.png) |
| Consulta con joins (`/loans/details`) | ![joins](capturas/11-loans-details.png) |
| Filtro por estado | ![status](capturas/12-filtro-status.png) |
| Filtro por tipo de dispositivo | ![tipo](capturas/13-filtro-device-type.png) |
| Prestamos de un usuario | ![usuario-loans](capturas/14-prestamos-usuario.png) |
| Devolucion del dispositivo | ![devolucion](capturas/15-devolucion.png) |
| Dispositivo nuevamente disponible | ![disponible](capturas/16-device-disponible.png) |
| Historial de prestamos del dispositivo | ![historial](capturas/17-historial-device.png) |

## 14. Reflexion sobre migraciones, relaciones y consultas avanzadas

Antes de Alembic, cada cambio en los modelos significaba borrar la base de datos y
volver a crearla, lo que en un proyecto real equivale a perder la informacion. Con
Alembic la estructura tiene **historia**: cada cambio queda en un archivo de la carpeta
`versions/`, se puede aplicar con `upgrade head` y revertir con `downgrade`. Eso permite
que el mismo cambio se aplique igual en mi maquina, en la de un compañero y en
produccion.

Las relaciones cambiaron la forma de pensar los datos. Antes cada tabla era una isla;
ahora `loans` conecta a `users` con `devices` mediante `ForeignKey`, y las
`relationship()` con `back_populates` me dejan navegar en ambos sentidos:
`usuario.loans` o `prestamo.device`. La integridad referencial garantiza que nunca
exista un prestamo "huerfano" apuntando a un usuario o dispositivo que no existe.

Las consultas con joins son las que le dan valor real a la API. Un `GET /loans` que solo
devuelve `user_id` y `device_id` obliga al cliente a hacer varias peticiones; en cambio
`GET /loans/details` responde en una sola llamada quien tiene prestado que equipo. Usar
`joinedload()` evita ademas el problema de las N+1 consultas.

Por ultimo, los filtros con `ilike()`, `and_()` y `or_()` me mostraron como construir
consultas dinamicas: la condicion solo se agrega si el query parameter llega, asi un
mismo endpoint sirve para buscar por estado, por correo, por tipo de dispositivo o por
texto libre. Junto con las reglas de negocio (no prestar un equipo ocupado, no devolver
dos veces) y los codigos `409 Conflict`, la API dejo de ser un CRUD y paso a modelar un
proceso real de prestamos.
