# device_systems — Seguridad, JWT, CORS, middleware y rate limiting (EV11)

**Evidencia:** [Proyecto-Final-v2] GA1-220501096-01-AA1-EV11 — FastAPI Seguridad
**Aprendiz:** Daniel Roman
**Version de la API:** 5.0.0
**Rama:** `device_systems_security` (unificada con `main`)

---

## 1. Descripcion

`device_systems` evoluciona a una API REST **segura**. Sobre la version 4.0.0
(Alembic + modelos relacionados + joins) se agregan mecanismos de seguridad
propios de una API profesional:

- Autenticacion **OAuth2** con **JWT** (algoritmo HS256).
- Hash de contrasenas con **bcrypt** via `passlib`.
- Autorizacion por **roles** (`admin`, `support`, `user`).
- Middleware personalizado (`X-App-Name`, `X-Process-Time`, `X-Request-ID`).
- **CORS** con lista blanca configurable via `.env`.
- **Rate limiting** con `slowapi` (limites por endpoint).
- Validaciones avanzadas con **Pydantic v2** (contrasenas seguras).

## 2. Tecnologias utilizadas

| Tecnologia | Uso |
|---|---|
| FastAPI 0.141 | Framework de la API |
| Uvicorn | Servidor ASGI |
| SQLAlchemy 2.x | ORM |
| Alembic | Migraciones de base de datos |
| Pydantic v2 | Validacion y schemas |
| passlib[bcrypt] | Hash de contrasenas |
| python-jose | Firma y verificacion de JWT |
| slowapi | Rate limiting |
| python-dotenv | Carga de configuracion desde `.env` |

## 3. Estructura del proyecto

```
device_systems/
│── app/
│   │── main.py                            # CORS, middleware, rate limiter, routers
│   │── config.py                          # carga variables de entorno (.env)
│   │── limiter.py                         # instancia global del Limiter (slowapi)
│   │
│   │── auth/                              # NUEVO
│   │   │── security.py                    # bcrypt (hash / verify) y JWT (encode / decode)
│   │   │── auth_service.py                # registro y autenticacion
│   │   │── auth_routes.py                 # /auth/register, /auth/login, /auth/me
│   │
│   │── database/connection.py             # engine, SessionLocal, Base
│   │
│   │── models/
│   │   │── user_model.py                  # + hashed_password
│   │   │── device_model.py
│   │   │── loan_model.py
│   │
│   │── schemas/
│   │   │── user_schema.py                 # + UserAdminCreate (con contrasena)
│   │   │── device_schema.py
│   │   │── loan_schema.py
│   │   │── auth_schema.py                 # NUEVO (UserRegister, UserLogin, Token, TokenData)
│   │
│   │── routes/
│   │   │── user_routes.py                 # protegido con Depends(auth)
│   │   │── device_routes.py               # roles admin/support
│   │   │── loan_routes.py                 # roles admin/support
│   │
│   │── services/
│   │   │── user_service.py                # + crear_usuario_admin(hashed_password)
│   │   │── device_service.py
│   │   │── loan_service.py
│   │
│   │── dependencies/
│   │   │── database_dependency.py         # get_db, get_user_or_404, ...
│   │   │── auth_dependency.py             # NUEVO (OAuth2, get_current_user, require_admin)
│   │
│   │── middlewares/                       # NUEVO
│   │   │── request_middleware.py          # X-App-Name, X-Process-Time, X-Request-ID
│
│── alembic/
│   │── versions/
│   │   │── 75b8b80c779a_create_users_table.py
│   │   │── e61a53a3b60c_create_devices_and_loans_tables.py
│   │   │── a3f14b9c2e01_add_authentication_fields_to_users.py    # NUEVO
│
│── .env.example
│── .env                     # (ignorado por git)
│── alembic.ini
│── requirements.txt
│── seed.py                  # crea 3 usuarios con contrasena "Segura123"
│── README.md
```

## 4. Instalacion

```bash
cd ev11/device_systems
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
copy .env.example .env       # Windows (cp en Linux/Mac)
```

Editar `.env` con la clave secreta real de la instalacion.

## 5. Ejecucion

```bash
alembic upgrade head         # aplica las 3 migraciones
python seed.py               # crea 3 usuarios y 4 dispositivos
uvicorn app.main:app --reload
```

Contrasena demo para los 3 usuarios sembrados: **`Segura123`**

| Usuario | Email | Rol |
|---|---|---|
| Ana Perez | ana@sena.edu.co | admin |
| Carlos Gomez | carlos@sena.edu.co | support |
| Laura Martinez | laura@sena.edu.co | user |

| Recurso | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| OpenAPI | http://127.0.0.1:8000/openapi.json |

## 6. Endpoints

### 6.1 Autenticacion `/auth`

| Metodo | Endpoint | Descripcion | Codigo |
|---|---|---|---|
| POST | `/auth/register` | Registro publico con contrasena segura | 201 |
| POST | `/auth/login` | Login OAuth2 (form-urlencoded) -> JWT | 200 |
| GET  | `/auth/me` | Perfil del usuario autenticado | 200 |

### 6.2 Recursos protegidos

| Ruta | Metodos | Proteccion |
|---|---|---|
| `/users` | GET | Usuario autenticado |
| `/users/{id}` | GET | Usuario autenticado |
| `/users/{id}/loans` | GET | Usuario autenticado |
| `/users` | POST | **Solo admin** (con contrasena) |
| `/users/{id}` | PUT, PATCH, DELETE | **Solo admin** |
| `/devices` | GET | Usuario autenticado |
| `/devices` | POST | **Admin o support** |
| `/devices/{id}` | PUT, PATCH | **Admin o support** |
| `/devices/{id}` | DELETE | **Solo admin** |
| `/loans` | GET, POST | Usuario autenticado |
| `/loans/details` | GET | **Admin o support** |
| `/loans/{id}/return` | PATCH | **Admin o support** |
| `/loans/{id}` | PATCH | **Admin o support** |

## 7. Codigos HTTP

| Situacion | Codigo |
|---|---|
| Creado | 201 Created |
| OK | 200 OK |
| Eliminado | 204 No Content |
| Token invalido/ausente | **401 Unauthorized** |
| Rol insuficiente | **403 Forbidden** |
| No encontrado | 404 Not Found |
| Regla de negocio | 409 Conflict |
| Duplicado | 400 Bad Request |
| Pydantic invalido | 422 Unprocessable Entity |
| Rate limit excedido | **429 Too Many Requests** |

## 8. Seguridad (detalles)

### 8.1 Hash de contrasenas (`app/auth/security.py`)

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

Ninguna contrasena se guarda ni se retorna en texto plano.
`UserResponse` no incluye el campo `hashed_password`.

### 8.2 Validacion de contrasena (Pydantic v2, `auth_schema.py`)

Reglas obligatorias:

- Minimo 8 caracteres.
- Al menos una **mayuscula**.
- Al menos una **minuscula**.
- Al menos un **numero**.
- **Sin espacios en blanco**.

Un `field_validator` rechaza cualquier contrasena que no cumpla con 422.

### 8.3 Emision del JWT (`app/auth/security.py`)

```python
def create_access_token(data: dict, expires_delta=None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
```

Payload almacenado:

```json
{"sub": "ana@sena.edu.co", "user_id": 1, "role": "admin", "exp": ..., "iat": ...}
```

### 8.4 Proteccion de rutas (`app/dependencies/auth_dependency.py`)

- `get_current_user` decodifica el JWT y lanza 401 si el token es invalido.
- `get_current_active_user` rechaza cuentas desactivadas (403).
- `require_roles(*roles)` es una **factory** de dependencia que exige uno
  de los roles dados. Se usa asi:

```python
require_admin              = require_roles(UserRole.ADMIN)
require_admin_or_support   = require_roles(UserRole.ADMIN, UserRole.SUPPORT)
```

### 8.5 CORS (`main.py`)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,   # lista blanca desde .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-App-Name", "X-Process-Time", "X-Request-ID"],
)
```

**Por que no `allow_origins=["*"]` con `allow_credentials=True`:** el
estandar CORS lo prohibe. Un origen comodin con credenciales permitiria
que cualquier sitio malicioso envie las cookies del usuario a la API,
abriendo la puerta a ataques CSRF y robo de sesion. En produccion se
debe listar unicamente el dominio del frontend real.

### 8.6 Middleware personalizado (`app/middlewares/request_middleware.py`)

```python
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        inicio = time.perf_counter()
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        response = await call_next(request)
        duracion = time.perf_counter() - inicio
        response.headers["X-App-Name"]     = "device_systems"
        response.headers["X-Process-Time"] = f"{duracion:.4f}"
        response.headers["X-Request-ID"]   = request_id
        logger.info("%s %s -> %d (%.4fs) [rid=%s]", ...)
        return response
```

### 8.7 Rate limiting (`app/limiter.py` + decoradores)

Limites aplicados:

| Endpoint | Limite |
|---|---|
| `POST /auth/register` | 3 / minuto |
| `POST /auth/login` | 5 / minuto |
| `GET  /users` | 30 / minuto |
| `POST /loans` | 10 / minuto |
| Todos los demas | 60 / minuto (default) |

Cuando se supera el limite, la API responde **HTTP 429** con el mensaje
`Limite de peticiones excedido: 5 per 1 minute`.

## 9. Ejemplos de uso

### 9.1 Registro publico

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Miguel Torres\",\"email\":\"miguel@sena.edu.co\",\"password\":\"Segura123\",\"role\":\"user\"}"
```

### 9.2 Login OAuth2 (form-urlencoded)

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=ana@sena.edu.co&password=Segura123"
```

Respuesta:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIi...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 9.3 Perfil autenticado

```bash
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### 9.4 Ruta protegida con rol

```bash
# Un usuario con rol "user" que intenta borrar dispositivo -> 403
curl -X DELETE http://127.0.0.1:8000/devices/1 \
  -H "Authorization: Bearer <token_user>"
```

## 10. Migracion Alembic aplicada

La migracion `a3f14b9c2e01_add_authentication_fields_to_users.py` agrega
la columna `hashed_password` a la tabla `users`.

```bash
alembic revision --autogenerate -m "add authentication fields to users"
alembic upgrade head
alembic history
```

## 11. Capturas de evidencia

Todas las capturas estan en `../cap evidencia/`.

| # | Evidencia | Captura |
|---|---|---|
| 1 | Estructura del proyecto | ![estructura](../cap%20evidencia/01-estructura-proyecto.png) |
| 2 | Migracion Alembic aplicada | ![alembic](../cap%20evidencia/02-alembic-migracion.png) |
| 3 | Registro de usuario | ![register](../cap%20evidencia/03-registro-usuario.png) |
| 4 | Login y token JWT generado | ![login](../cap%20evidencia/04-login-token.png) |
| 5 | GET /auth/me | ![me](../cap%20evidencia/05-auth-me.png) |
| 6 | Acceso sin token (401) | ![sin token](../cap%20evidencia/06-sin-token.png) |
| 7 | Acceso con rol no permitido (403) | ![403](../cap%20evidencia/07-rol-no-permitido.png) |
| 8 | Swagger UI con OAuth2 | ![swagger](../cap%20evidencia/08-swagger-oauth2.png) |
| 9 | ReDoc | ![redoc](../cap%20evidencia/09-redoc.png) |
| 10 | Cabeceras del middleware | ![headers](../cap%20evidencia/10-cabeceras-middleware.png) |
| 11 | Rate limiting activado (429) | ![429](../cap%20evidencia/11-rate-limit-429.png) |

## 12. Pruebas funcionales realizadas

| # | Prueba | Esperado | Resultado |
|---|---|---|---|
| 1 | Registro de usuario valido | 201 | OK |
| 2 | Registro con contrasena debil | 422 | OK |
| 3 | Registro con email duplicado | 400 | OK |
| 4 | Login correcto | 200 + token | OK |
| 5 | Login con contrasena incorrecta | 401 | OK |
| 6 | Consulta de /auth/me | 200 | OK |
| 7 | Acceso a ruta protegida sin token | 401 | OK |
| 8 | Acceso con token invalido | 401 | OK |
| 9 | Acceso con usuario sin permisos (rol user borra dispositivo) | 403 | OK |
| 10 | Creacion de dispositivo con rol admin | 201 | OK |
| 11 | Eliminacion de dispositivo con rol user | 403 | OK |
| 12 | Configuracion CORS activa | Origen permitido pasa, otro es rechazado | OK |
| 13 | Cabeceras generadas por middleware | X-App-Name, X-Process-Time, X-Request-ID presentes | OK |
| 14 | Activacion de rate limiting en /auth/login | 429 al 6to intento | OK |
| 15 | Verificacion de Swagger/OpenAPI | Endpoints con OAuth2 y candado | OK |

## 13. Reflexion final

Antes de esta version, `device_systems` estaba abierto a cualquier cliente:
cualquiera podia listar usuarios, crear dispositivos o borrar prestamos. Al
agregar la capa de seguridad la API paso de "funcional" a "publicable".

Lo que mas cambio fue **como pienso los endpoints**. Ya no basta con
implementar el flujo feliz; hay que decidir para cada ruta quien puede
llamarla, con que rol, cuantas veces por minuto y bajo que cabecera de
autenticacion. La factory `require_roles(...)` fue una idea que se repitio
mucho: en vez de escribir un if de rol en cada endpoint, la logica vive
en un solo lugar y las rutas quedan legibles con
`Depends(require_admin_or_support)`.

Del lado de las contrasenas, el patron es simple pero muy claro: la
contrasena entra en `UserRegister`, Pydantic verifica la fortaleza,
`passlib` la hashea con bcrypt y a la base de datos solo llega el hash.
El `UserResponse` no incluye `hashed_password`, asi que aunque yo olvide
excluirlo manualmente, nunca se filtra. Esa separacion entre modelo
SQLAlchemy y schema Pydantic termino siendo la mejor defensa contra
filtrar informacion sensible.

Con JWT aprendi que el token es basicamente una firma sobre un payload:
FastAPI decodifica, verifica que el `exp` no haya pasado y valida la firma
con la `SECRET_KEY`. Si algo falla, `python-jose` lanza `JWTError` y la
dependencia lo traduce a 401. No hay estado en el servidor: eso hace la
API mas facil de escalar, pero tambien mas dependiente de proteger la
clave (por eso vive en `.env`, ignorado por git).

El middleware personalizado y el rate limiting me mostraron el otro
lado de la seguridad: **observabilidad y proteccion contra abuso**. El
`X-Request-ID` permite trazar una peticion en logs; el `X-Process-Time`
sirve para detectar endpoints lentos; el rate limit de `slowapi` frena
un ataque de fuerza bruta con muy pocas lineas de codigo.

Finalmente, configurar CORS con lista blanca me obligo a pensar quien es
el "cliente legitimo" de la API. Un `allow_origins=["*"]` con
`allow_credentials=True` deja la puerta abierta a que cualquier pagina
web use las cookies del usuario para llamar a la API en su nombre. Por
eso el `.env.example` deja los origenes en `localhost` para desarrollo
y el README recuerda que en produccion **hay que listar solo el dominio
real del frontend**. La seguridad no es una libreria: es una serie de
decisiones pequenas que solo aparecen cuando la API pasa del "codigo
que funciona" al "codigo que va a servir a otros".
