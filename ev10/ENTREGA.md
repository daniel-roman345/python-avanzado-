# Entrega EV10 — FastAPI Avanzado (Alembic, relaciones y joins)

**Guia:** [Proyecto-Final-v1] GA1-220501096-01-AA1-EV10 · **Duracion:** 6 horas
**Proyecto:** [`device_systems/`](device_systems/) · **README:** [device_systems/README.md](device_systems/README.md)
**Rama pedida:** `device_systems_alembic_relaciones` (creada y unificada con `main`)

## Checklist de evidencias

| # | Evidencia pedida | Donde esta | Estado |
|---|---|---|---|
| 1 | Proyecto `device_systems` actualizado | `ev10/device_systems/` | Listo |
| 2 | Rama `device_systems_alembic_relaciones` unificada con `main` | historial de git | Listo |
| 3 | Configuracion de Alembic | `alembic.ini` y `alembic/env.py` | Listo |
| 4 | Carpeta `alembic/versions` con migraciones | `75b8b80c779a_create_users_table.py`, `e61a53a3b60c_create_devices_and_loans_tables.py` | Listo |
| 5 | Modelos `User`, `Device` y `Loan` | `app/models/` | Listo |
| 6 | Asociaciones (`ForeignKey`, `relationship`, `back_populates`) | `app/models/loan_model.py` | Listo |
| 7 | Schemas Pydantic de los 3 recursos | `app/schemas/` | Listo |
| 8 | CRUD de usuarios y dispositivos | `app/routes/user_routes.py`, `device_routes.py` | Listo |
| 9 | Gestion de prestamos (crear, devolver, estados) | `app/routes/loan_routes.py` | Listo |
| 10 | Consultas con joins y filtros avanzados | `app/services/loan_service.py`, `device_service.py` | Listo |
| 11 | Manejo de errores y reglas de negocio (`409 Conflict`) | `app/main.py` y rutas | Listo |
| 12 | README.md actualizado | `device_systems/README.md` | Listo |
| 13 | Capturas de Alembic, tablas, Swagger, joins, filtros y devolucion | `device_systems/capturas/` | **Pendiente: tomarlas** |

## Lo unico que falta hacer manualmente

```bash
cd ev10/device_systems
pip install -r requirements.txt
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

Para las capturas de Alembic (01 a 04) ejecuta y captura la salida de:

```bash
alembic history
```

Las migraciones ya estan generadas; si quieres capturar el `revision --autogenerate`
en vivo, crea un cambio pequeno en un modelo y vuelve a generarla.

Tomar las 17 capturas listadas en `device_systems/capturas/LEEME.txt`.

## Guion para la socializacion (5 minutos)

1. **Cambios frente a la version anterior:** dos recursos nuevos (`devices`,
   `loans`) y control de versiones de la base de datos.
2. **Configuracion de Alembic:** `alembic init`, `sqlalchemy.url` en
   `alembic.ini` y `target_metadata = Base.metadata` en `env.py`.
3. **Migraciones generadas:** `create users table` y
   `create devices and loans tables`; aplicadas con `upgrade head`.
4. **Relaciones:** `User` 1-N `Loan` N-1 `Device`, con `ForeignKey()` y
   `relationship(back_populates=...)`.
5. **Joins:** `GET /loans/details`, `GET /users/{id}/loans` y
   `GET /devices/{id}/loans` devuelven usuario + dispositivo en una sola consulta
   gracias a `joinedload()`.
6. **Filtros avanzados:** `ilike()`, `and_()`, `or_()` y condiciones opcionales.
7. **Que aprendi:** modelado relacional, integridad referencial y por que las
   migraciones evitan perder datos.
