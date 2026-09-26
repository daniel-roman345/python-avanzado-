# Entrega EV11 — FastAPI Seguridad (autenticacion, middleware, CORS, rate limiting)

**Guia:** [Proyecto-Final-v2] GA1-220501096-01-AA1-EV11 · **Duracion:** 12 horas
**Proyecto:** [`device_systems/`](device_systems/) · **README:** [device_systems/README.md](device_systems/README.md)
**Rama:** `device_systems_security` (unificada con `main`)

## Checklist de evidencias

| # | Evidencia | Donde esta | Estado |
|---|---|---|---|
| 1 | Proyecto `device_systems` actualizado | `ev11/device_systems/` | Listo |
| 2 | Autenticacion OAuth2 y JWT | `app/auth/` | Listo |
| 3 | Registro y login de usuarios | `POST /auth/register`, `POST /auth/login` | Listo |
| 4 | Hash de contrasenas con passlib | `app/auth/security.py` (bcrypt) | Listo |
| 5 | Rutas protegidas por token | `Depends(get_current_active_user)` | Listo |
| 6 | Roles y autorizacion basica | `require_admin`, `require_admin_or_support` | Listo |
| 7 | Middleware personalizado | `app/middlewares/request_middleware.py` | Listo |
| 8 | Configuracion CORS | `CORSMiddleware` en `main.py` | Listo |
| 9 | Rate limiting | `app/limiter.py` + decoradores en rutas | Listo |
| 10 | Validaciones avanzadas Pydantic v2 | `app/schemas/auth_schema.py` | Listo |
| 11 | Migracion Alembic para auth | `alembic/versions/a3f14b9c2e01_...` | Listo |
| 12 | README.md actualizado | `device_systems/README.md` | Listo |
| 13 | Archivo `.env.example` | `device_systems/.env.example` | Listo |
| 14 | Capturas de evidencia | `cap evidencia/` (01 a 11) | Listo |

## Como ejecutar el proyecto

```bash
cd ev11/device_systems
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

Contrasena demo para los 3 usuarios: **`Segura123`**
- ana@sena.edu.co (admin)
- carlos@sena.edu.co (support)
- laura@sena.edu.co (user)

Abrir Swagger UI: http://127.0.0.1:8000/docs

## Guion para la socializacion (max 15 minutos, video de youtube)

1. **Demo funcional** (3 min): registrar usuario, login, mostrar el token JWT,
   `/auth/me`, listar dispositivos con token, crear dispositivo con rol admin.
2. **Que cambio respecto a EV10** (2 min): capa `auth/`, campo
   `hashed_password`, dependencias de autorizacion, middleware, CORS, rate limit.
3. **Como protegio las rutas** (2 min): `get_current_user` -> `require_roles`
   como factory -> `require_admin` / `require_admin_or_support`.
4. **Hash de contrasenas** (1 min): `passlib.CryptContext(schemes=["bcrypt"])`;
   nunca se guarda ni se retorna la contrasena en texto plano.
5. **OAuth2 + JWT** (2 min): `OAuth2PasswordBearer(tokenUrl="/auth/login")`,
   `python-jose` firma con `HS256`, `SECRET_KEY` desde `.env`, `exp` obligatorio.
6. **Middleware y CORS** (2 min): mostrar `X-App-Name`, `X-Process-Time`,
   `X-Request-ID` en la respuesta y explicar la lista blanca de CORS.
7. **Rate limiting** (1 min): 6 intentos de login para ver el 429.
8. **Aprendizaje** (2 min): la seguridad son decisiones pequenas
   por endpoint, no una libreria.
