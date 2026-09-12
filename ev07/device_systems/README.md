# device_systems — API REST de Usuarios (EV07)

**Evidencia:** GA1-220501096-01-AA1-EV07 — Fundamentos de FastAPI
**Aprendiz:** Daniel Roman
**Version de la API:** 1.0.0

---

## 1. Descripcion de la aplicacion

`device_systems` es una aplicacion backend construida con **FastAPI** que expone una
**API REST** para administrar los usuarios del sistema. En esta primera version la
informacion se almacena en memoria (una lista de diccionarios) y la API permite:

- Listar todos los usuarios.
- Consultar un usuario por su **ID** (path parameter).
- Filtrar usuarios por **rol** y por **estado activo** (query parameters).
- Registrar nuevos usuarios validando los datos con **Pydantic v2**.
- Evitar correos duplicados.
- Devolver respuestas estandarizadas mediante **response models**.
- Enviar **cabeceras HTTP personalizadas** (`X-App-Name`, `X-API-Version`).

## 2. Estructura del proyecto

```
device_systems/
│── app/
│   │── __init__.py
│   │── main.py                 # Creacion de la app, metadatos y middleware de cabeceras
│   │── schemas/
│   │   │── user_schema.py      # Modelos Pydantic v2 (entrada y salida)
│   │── routes/
│   │   │── user_routes.py      # Endpoints GET y POST del recurso users
│── capturas/                   # Capturas de Swagger UI y pruebas
│── requirements.txt
│── README.md
```

| Carpeta | Responsabilidad |
|---|---|
| `app/schemas` | Modelos Pydantic de entrada (`UserCreate`) y de salida (`UserResponse`) |
| `app/routes` | Definicion de los endpoints del recurso `/users` |
| `app/main.py` | Configuracion de FastAPI, metadatos de Swagger y cabeceras HTTP |

## 3. Instalacion de dependencias

```bash
cd ev07/device_systems
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Contenido de `requirements.txt`:

```
fastapi
uvicorn[standard]
pydantic>=2
email-validator
```

## 4. Ejecucion del servidor

```bash
uvicorn app.main:app --reload
```

| Recurso | URL |
|---|---|
| API | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| Esquema OpenAPI | http://127.0.0.1:8000/openapi.json |

## 5. Modelo de usuario y validaciones

| Campo | Tipo | Validacion |
|---|---|---|
| `id` | `int` | Generado automaticamente, solo aparece en la respuesta |
| `name` | `str` | Obligatorio, minimo 3 caracteres (`Field(min_length=3)`) |
| `email` | `EmailStr` | Obligatorio, formato de correo valido |
| `role` | `UserRole` | Solo acepta `admin`, `support` o `user` |
| `is_active` | `bool` | Booleano, por defecto `true` |

Modelos definidos en `app/schemas/user_schema.py`:

| Modelo | Uso |
|---|---|
| `UserRole` | Enum con los roles permitidos |
| `UserBase` | Campos comunes + validador de nombre |
| `UserCreate` | **Entrada** del POST |
| `UserResponse` | **Salida**: expone solo los datos publicos del usuario |
| `UserListResponse` | Respuesta estandarizada `{ total, data }` |

## 6. Tabla de endpoints

| Metodo | Endpoint | Descripcion | Codigo exitoso |
|---|---|---|---|
| `GET` | `/` | Informacion general de la API | `200 OK` |
| `GET` | `/users` | Lista todos los usuarios | `200 OK` |
| `GET` | `/users?role=admin` | Filtra por rol (query parameter) | `200 OK` |
| `GET` | `/users?is_active=true` | Filtra por estado (query parameter) | `200 OK` |
| `GET` | `/users/{user_id}` | Consulta un usuario por ID (path parameter) | `200 OK` |
| `POST` | `/users` | Registra un nuevo usuario | `201 Created` |

### Codigos de error

| Situacion | Codigo |
|---|---|
| Usuario no encontrado | `404 Not Found` |
| Correo ya registrado | `400 Bad Request` |
| Datos invalidos (Pydantic) | `422 Unprocessable Entity` |

## 7. Cabeceras HTTP personalizadas

Un **middleware** en `app/main.py` agrega a **todas** las respuestas:

```
X-App-Name: device_systems
X-API-Version: 1.0
```

Ademas:

- `GET /users` agrega `X-Total-Users` con la cantidad de registros devueltos.
- `POST /users` agrega `Location: /users/{id}` con la ruta del recurso creado.

## 8. Ejemplos de peticiones y respuestas

### 8.1 GET /users

```bash
curl -i http://127.0.0.1:8000/users
```

```http
HTTP/1.1 200 OK
x-total-users: 3
x-app-name: device_systems
x-api-version: 1.0
```

```json
{
  "total": 3,
  "data": [
    { "id": 1, "name": "Ana Perez", "email": "ana@sena.edu.co", "role": "admin", "is_active": true },
    { "id": 2, "name": "Carlos Gomez", "email": "carlos@sena.edu.co", "role": "support", "is_active": true },
    { "id": 3, "name": "Laura Martinez", "email": "laura@sena.edu.co", "role": "user", "is_active": false }
  ]
}
```

### 8.2 GET /users?role=admin (Query Parameter)

```bash
curl "http://127.0.0.1:8000/users?role=admin"
```

```json
{
  "total": 1,
  "data": [
    { "id": 1, "name": "Ana Perez", "email": "ana@sena.edu.co", "role": "admin", "is_active": true }
  ]
}
```

### 8.3 GET /users?is_active=false

```bash
curl "http://127.0.0.1:8000/users?is_active=false"
```

```json
{
  "total": 1,
  "data": [
    { "id": 3, "name": "Laura Martinez", "email": "laura@sena.edu.co", "role": "user", "is_active": false }
  ]
}
```

### 8.4 GET /users/{user_id} (Path Parameter)

```bash
curl http://127.0.0.1:8000/users/1
```

```json
{ "id": 1, "name": "Ana Perez", "email": "ana@sena.edu.co", "role": "admin", "is_active": true }
```

### 8.5 GET /users/99 — usuario inexistente

```json
HTTP 404
{ "detail": "Usuario no encontrado" }
```

### 8.6 POST /users

```bash
curl -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" -d "{\"name\":\"Pedro Ruiz\",\"email\":\"pedro@sena.edu.co\",\"role\":\"user\",\"is_active\":true}"
```

```json
HTTP 201 Created
Location: /users/4

{ "id": 4, "name": "Pedro Ruiz", "email": "pedro@sena.edu.co", "role": "user", "is_active": true }
```

### 8.7 POST /users — correo duplicado

```json
HTTP 400
{ "detail": "El correo ya esta registrado" }
```

### 8.8 POST /users — datos invalidos (validacion Pydantic)

Cuerpo enviado:

```json
{ "name": "ab", "email": "malo", "role": "root" }
```

Respuesta:

```json
HTTP 422
{
  "detail": [
    { "loc": ["body", "name"],  "msg": "String should have at least 3 characters" },
    { "loc": ["body", "email"], "msg": "value is not a valid email address" },
    { "loc": ["body", "role"],  "msg": "Input should be 'admin', 'support' or 'user'" }
  ]
}
```

## 9. Pruebas realizadas

| # | Prueba | Resultado esperado | Resultado |
|---|---|---|---|
| 1 | `GET /users` | `200` + 3 usuarios | OK |
| 2 | `GET /users?role=admin` | `200` + 1 usuario | OK |
| 3 | `GET /users?is_active=false` | `200` + 1 usuario | OK |
| 4 | `GET /users/1` | `200` + usuario Ana Perez | OK |
| 5 | `GET /users/99` | `404` "Usuario no encontrado" | OK |
| 6 | `POST /users` valido | `201` + usuario creado | OK |
| 7 | `POST /users` correo repetido | `400` | OK |
| 8 | `POST /users` datos invalidos | `422` con 3 errores | OK |
| 9 | Cabeceras `X-App-Name` / `X-API-Version` | Presentes en toda respuesta | OK |

## 10. Capturas de Swagger UI

> Guarda las imagenes en la carpeta `capturas/` con estos nombres y se veran aqui.

| Evidencia | Captura |
|---|---|
| Swagger UI completo | ![Swagger UI](capturas/01-swagger-ui.png) |
| GET /users | ![GET users](capturas/02-get-users.png) |
| GET /users/{user_id} | ![GET user id](capturas/03-get-user-id.png) |
| GET usuario inexistente (404) | ![404](capturas/04-get-user-404.png) |
| POST /users (201) | ![POST users](capturas/05-post-users.png) |
| POST correo duplicado (400) | ![Duplicado](capturas/06-post-duplicado.png) |
| POST datos invalidos (422) | ![Invalido](capturas/07-post-invalido.png) |
| Cabeceras personalizadas | ![Headers](capturas/08-headers.png) |

## 11. Reflexion sobre el uso de FastAPI

Construir esta API me mostro que FastAPI resuelve con muy poco codigo tareas que
normalmente son repetitivas. Al declarar los tipos en la firma de la funcion, el
framework se encarga solo de leer el path parameter, convertir el query parameter
a `bool` o a `Enum`, validar el cuerpo de la peticion y devolver un `422` con el
detalle exacto del error, sin que yo escriba una sola linea de validacion manual.

Pydantic v2 es la pieza central: separar `UserCreate` de `UserResponse` permite
controlar que entra y que sale de la API, ocultando datos que no deben exponerse.
Ademas, los `response_model` alimentan automaticamente la documentacion OpenAPI,
de manera que Swagger UI se convierte en una herramienta de prueba real y no solo
en documentacion.

Finalmente, el middleware para las cabeceras `X-App-Name` y `X-API-Version` me
dejo ver como FastAPI (sobre Starlette) permite interceptar todas las peticiones
en un solo punto, algo clave para trazabilidad, versionado y seguridad en las
siguientes versiones de `device_systems`.
