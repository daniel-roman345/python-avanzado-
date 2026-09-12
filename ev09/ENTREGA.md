# Entrega EV09 — FastAPI con SQLAlchemy (persistencia y CRUD en base de datos)

**Guia:** GA1-220501096-01-AA1-EV09 · **Duracion:** 12 horas
**Proyecto:** [`device_systems/`](device_systems/) · **README:** [device_systems/README.md](device_systems/README.md)

## Checklist de evidencias

| # | Evidencia pedida | Donde esta | Estado |
|---|---|---|---|
| 1 | Proyecto `device_systems` actualizado | `ev09/device_systems/` | Listo |
| 2 | Conexion con SQLAlchemy (engine, SessionLocal, Base) | `app/database/connection.py` | Listo |
| 3 | Modelo SQLAlchemy `User` con constraints | `app/models/user_model.py` | Listo |
| 4 | Schemas Pydantic (Create, Update, Patch, Response) | `app/schemas/user_schema.py` | Listo |
| 5 | Dependencia `get_db()` con `yield` | `app/dependencies/database_dependency.py` | Listo |
| 6 | CRUD completo sobre base de datos + filtros y orden | `app/services/user_service.py` | Listo |
| 7 | Endpoints GET, POST, PUT, PATCH, DELETE | `app/routes/user_routes.py` | Listo |
| 8 | Manejo de errores y codigos HTTP | `app/main.py` (incluye `IntegrityError` → 400) | Listo |
| 9 | Documentacion Swagger/OpenAPI | `/docs` y `/redoc` | Listo |
| 10 | `requirements.txt` | `device_systems/requirements.txt` | Listo |
| 11 | README.md actualizado (incluye diferencia modelo vs schema) | `device_systems/README.md` | Listo |
| 12 | Capturas: estructura, base de datos generada, Swagger y pruebas | `device_systems/capturas/` | **Pendiente: tomarlas** |

## Lo unico que falta hacer manualmente

```bash
cd ev09/device_systems
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```

- La base `device_systems.db` ya se genera sola (tambien al arrancar la app).
- Para la captura de la base de datos puedes usar la extension **SQLite Viewer**
  de VS Code o **DB Browser for SQLite**.
- Tomar las 14 capturas listadas en `device_systems/capturas/LEEME.txt`.

## Guion para la socializacion (5 minutos)

1. **Cambios frente a la version anterior:** los datos dejaron de vivir en memoria.
2. **Configuracion de SQLAlchemy:** `DATABASE_URL`, `create_engine`,
   `sessionmaker` y `DeclarativeBase`.
3. **Modelo `User`:** columnas con `unique=True`, `nullable=False`, `default` y
   `created_at`.
4. **Modelo vs schema:** el modelo describe la tabla, el schema describe el
   contrato HTTP; `from_attributes=True` conecta los dos.
5. **CRUD sobre base de datos:** `add/commit/refresh`, `db.get()`, `select()`,
   `delete()`, filtros con `where()` y orden con `order_by()`.
6. **Validaciones y constraints:** Pydantic devuelve `422`, la base protege con
   `unique` y el manejador de `IntegrityError` lo traduce a `400`.
7. **Que aprendi:** la persistencia y la dependencia `get_db()` con `yield`.
