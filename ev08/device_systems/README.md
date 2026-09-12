# device_systems — CRUD completo, errores y Dependency Injection (EV08)

**Evidencia:** GA1-220501096-01-AA1-EV08 — FastAPI Intermedio
**Aprendiz:** Daniel Roman
**Version de la API:** 2.0.0

---

## 1. Descripcion de la API

`device_systems` evoluciona desde la version 1.0 (solo `GET` y `POST`) hacia una API
REST profesional con **CRUD completo** del recurso `/users`. Los datos siguen
almacenandose en memoria, pero ahora la aplicacion:

- Implementa `PUT`, `PATCH` y `DELETE` ademas de `GET` y `POST`.
- Maneja errores con `HTTPException` y devuelve respuestas **estructuradas**.
- Usa los **codigos de estado HTTP** correctos en cada operacion.
- Reutiliza logica mediante **Dependency Injection** (`Depends()`).
- Separa responsabilidades en capas: `routes`, `schemas`, `services`,
  `dependencies` y `data`.
- Mejora la documentacion automatica **Swagger/OpenAPI** con tags, `summary`,
  `description` y `response_description`.

## 2. Tecnologias utilizadas

| Tecnologia | Uso |
|---|---|
| Python 3.x | Lenguaje base |
| FastAPI | Framework de la API REST |
| Pydantic v2 | Validacion de datos y modelos de entrada/salida |
| Uvicorn | Servidor ASGI |
| Swagger UI / ReDoc | Documentacion automatica |

## 3. Estructura del proyecto

```
device_systems/
│── app/
│   │── main.py                        # App, metadatos, middleware y manejadores de error
│   │
│   │── routes/
│   │   │── user_routes.py             # Endpoints del recurso users
│   │
│   │── schemas/
│   │   │── user_schema.py             # UserCreate, UserUpdate, UserPatch, UserResponse...
│   │
│   │── services/
│   │   │── user_service.py            # Logica de negocio (sin FastAPI)
│   │
│   │── dependencies/
│   │   │── user_dependencies.py       # Funciones reutilizables con Depends()
│   │
│   │── data/
│   │   │── users_db.py                # Base de datos simulada en memoria
│
│── capturas/
│── requirements.txt
│── README.md
```

| Capa | Responsabilidad |
|---|---|
| `routes` | Definen los endpoints y los codigos HTTP; no contienen logica de negocio |
| `schemas` | Modelos Pydantic de entrada y salida |
| `services` | Logica de negocio pura sobre la base en memoria |
| `dependencies` | Validaciones y busquedas reutilizables inyectadas con `Depends()` |
| `data` | Simulacion de la base de datos |

## 4. Instalacion y ejecucion

```bash
cd ev08/device_systems
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

| Recurso | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| OpenAPI | http://127.0.0.1:8000/openapi.json |

## 5. Tabla de endpoints

| Metodo | Endpoint | Descripcion | Codigo exitoso | Errores |
|---|---|---|---|---|
| `GET` | `/` | Informacion de la API (usa `Depends(get_api_settings)`) | `200` | — |
| `GET` | `/health` | Estado del servicio | `200` | — |
| `GET` | `/users` | Lista usuarios | `200` | `400` rol invalido |
| `GET` | `/users?role=admin` | Filtra por rol | `200` | `400` |
| `GET` | `/users?is_active=true` | Filtra por estado | `200` | — |
| `GET` | `/users/{user_id}` | Consulta por ID | `200` | `404` |
| `POST` | `/users` | Crea un usuario | `201` | `400`, `422` |
| `PUT` | `/users/{user_id}` | Actualiza **todos** los campos | `200` | `404`, `400`, `422` |
| `PATCH` | `/users/{user_id}` | Actualiza **algunos** campos | `200` | `404`, `400`, `422` |
| `DELETE` | `/users/{user_id}` | Elimina el usuario | `200` | `404` |

## 6. Codigos de estado HTTP aplicados

| Operacion | Metodo | Codigo |
|---|---|---|
| Listar usuarios | `GET /users` | `200 OK` |
| Consultar usuario | `GET /users/{user_id}` | `200 OK` |
| Crear usuario | `POST /users` | `201 Created` |
| Actualizar completo | `PUT /users/{user_id}` | `200 OK` |
| Actualizar parcial | `PATCH /users/{user_id}` | `200 OK` |
| Eliminar usuario | `DELETE /users/{user_id}` | `200 OK` + mensaje |
| Usuario no encontrado | Cualquiera por ID | `404 Not Found` |
| Correo duplicado | `POST` / `PUT` / `PATCH` | `400 Bad Request` |
| PATCH sin datos | `PATCH` | `400 Bad Request` |
| Rol no permitido (query) | `GET /users?role=` | `400 Bad Request` |
| Datos invalidos | Validacion Pydantic | `422 Unprocessable Entity` |

## 7. Manejo de errores implementado

Toda la API responde los errores con un **formato unico** gracias a dos manejadores
registrados en `app/main.py`:

```python
@app.exception_handler(HTTPException)
async def manejar_http_exception(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
        },
    )
```

Casos controlados:

| Caso | Donde se controla | Respuesta |
|---|---|---|
| Usuario no encontrado | `get_user_or_404` | `404` `"Usuario no encontrado"` |
| Correo duplicado al crear | `validar_email_unico` | `400` `"El correo ya esta registrado"` |
| Correo de otro usuario al actualizar | `validar_email_unico_en_actualizacion` | `400` |
| PATCH sin datos | `validar_patch_no_vacio` | `400` `"Debe enviar al menos un campo para actualizar"` |
| Rol no permitido | `validar_rol_permitido` | `400` con la lista de roles validos |
| Eliminar usuario inexistente | `get_user_or_404` | `404` |
| Datos invalidos | `RequestValidationError` | `422` con campo y mensaje |

Ejemplo de respuesta de error:

```json
{
  "error": true,
  "message": "Usuario no encontrado",
  "status_code": 404,
  "path": "/users/99"
}
```

## 8. Uso de Depends() — Dependency Injection

Las dependencias viven en `app/dependencies/user_dependencies.py` y se reutilizan en
varias rutas, evitando repetir codigo:

| Dependencia | Que hace | Endpoints que la usan |
|---|---|---|
| `get_user_or_404(user_id)` | Busca el usuario y lanza `404` si no existe | `GET`, `PUT`, `PATCH`, `DELETE` por ID |
| `validar_email_unico(usuario)` | Impide crear correos duplicados | `POST /users` |
| `validar_email_unico_en_actualizacion(...)` | Impide que un `PUT` repita el correo de otro usuario | `PUT /users/{id}` |
| `validar_patch_no_vacio(...)` | Devuelve `400` si el `PATCH` llega vacio | `PATCH /users/{id}` |
| `validar_rol_permitido(role)` | Valida el rol del query parameter y responde `400` | `GET /users` |
| `get_api_settings()` | Entrega la configuracion general de la API | `GET /` |
| `verificar_api_key(x_api_key)` | Autenticacion basica simulada por cabecera | disponible para proteger rutas |

Ejemplo:

```python
def get_user_or_404(user_id: int = Path(..., ge=1)) -> Dict:
    usuario = user_service.obtener_por_id(user_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.get("/{user_id}", response_model=UserResponse)
def obtener_usuario(usuario: Dict = Depends(get_user_or_404)):
    return UserResponse(**usuario)
```

La ventaja es clara: la busqueda y el `404` se escriben **una sola vez** y los cuatro
endpoints por ID los heredan; ademas FastAPI documenta el parametro automaticamente.

## 9. Documentacion Swagger/OpenAPI

Metadatos configurados en `app/main.py`:

```python
app = FastAPI(
    title="device_systems API",
    description="API REST para la gestion de usuarios del sistema device_systems",
    version="2.0.0",
    contact={"name": "Daniel Roman - Aprendiz SENA", "email": "daniel992007@gmail.com"},
    openapi_tags=tags_metadata,
)
```

- Los endpoints se agrupan con `tags=["Users"]` y `tags=["Root"]`.
- Cada endpoint declara `summary`, `description`, `response_description` y el
  diccionario `responses` con los codigos de error posibles.

## 10. Ejemplos de peticiones y respuestas

### 10.1 PUT /users/2 — actualizacion completa

```bash
curl -X PUT http://127.0.0.1:8000/users/2 -H "Content-Type: application/json" -d "{\"name\":\"Carlos A Gomez\",\"email\":\"carlos.g@sena.edu.co\",\"role\":\"admin\",\"is_active\":false}"
```

```json
HTTP 200 OK
{ "id": 2, "name": "Carlos A Gomez", "email": "carlos.g@sena.edu.co", "role": "admin", "is_active": false }
```

### 10.2 PUT /users/99 — usuario inexistente

```json
HTTP 404
{ "error": true, "message": "Usuario no encontrado", "status_code": 404, "path": "/users/99" }
```

### 10.3 PATCH /users/3 — actualizacion parcial

Cuerpo enviado:

```json
{ "role": "support" }
```

```json
HTTP 200 OK
{ "id": 3, "name": "Laura Martinez", "email": "laura@sena.edu.co", "role": "support", "is_active": false }
```

### 10.4 PATCH /users/3 — cuerpo vacio

```json
HTTP 400
{ "error": true, "message": "Debe enviar al menos un campo para actualizar", "status_code": 400, "path": "/users/3" }
```

### 10.5 DELETE /users/4

```json
HTTP 200 OK
{ "message": "Usuario 4 eliminado correctamente" }
```

### 10.6 DELETE /users/4 — segundo intento

```json
HTTP 404
{ "error": true, "message": "Usuario no encontrado", "status_code": 404, "path": "/users/4" }
```

### 10.7 GET /users?role=root — rol no permitido

```json
HTTP 400
{ "error": true, "message": "Rol no permitido. Valores validos: admin, support, user", "status_code": 400, "path": "/users" }
```

### 10.8 POST /users — datos invalidos

```json
HTTP 422
{
  "error": true,
  "message": "Error de validacion en los datos enviados",
  "status_code": 422,
  "detail": [
    { "campo": "body.name",  "mensaje": "String should have at least 3 characters" },
    { "campo": "body.email", "mensaje": "value is not a valid email address" },
    { "campo": "body.role",  "mensaje": "Input should be 'admin', 'support' or 'user'" }
  ]
}
```

## 11. Pruebas funcionales realizadas

| # | Prueba | Esperado | Resultado |
|---|---|---|---|
| 1 | `GET /users` | `200` + 3 usuarios | OK |
| 2 | `GET /users?role=admin` | `200` + 1 usuario | OK |
| 3 | `GET /users?is_active=true` | `200` + 2 usuarios | OK |
| 4 | `GET /users/2` | `200` | OK |
| 5 | `GET /users/99` | `404` | OK |
| 6 | `POST /users` valido | `201` | OK |
| 7 | `POST /users` correo repetido | `400` | OK |
| 8 | `POST /users` datos invalidos | `422` | OK |
| 9 | `PUT /users/2` | `200` | OK |
| 10 | `PUT /users/99` | `404` | OK |
| 11 | `PUT` con correo de otro usuario | `400` | OK |
| 12 | `PATCH /users/3` con `{"role":"support"}` | `200` | OK |
| 13 | `PATCH /users/3` con `{}` | `400` | OK |
| 14 | `PATCH /users/99` | `404` | OK |
| 15 | `DELETE /users/4` | `200` + mensaje | OK |
| 16 | `DELETE /users/4` repetido | `404` | OK |
| 17 | `GET /users?role=root` | `400` | OK |

## 12. Capturas

> Guarda las imagenes en `capturas/` con estos nombres.

| Evidencia | Captura |
|---|---|
| Swagger UI (/docs) | ![Swagger](capturas/01-swagger-ui.png) |
| ReDoc (/redoc) | ![ReDoc](capturas/02-redoc.png) |
| GET /users | ![GET](capturas/03-get-users.png) |
| GET /users/{user_id} | ![GET id](capturas/04-get-user-id.png) |
| POST /users (201) | ![POST](capturas/05-post-users.png) |
| PUT /users/{user_id} (200) | ![PUT](capturas/06-put-user.png) |
| PATCH /users/{user_id} (200) | ![PATCH](capturas/07-patch-user.png) |
| DELETE /users/{user_id} | ![DELETE](capturas/08-delete-user.png) |
| Usuario inexistente (404) | ![404](capturas/09-error-404.png) |
| PATCH vacio (400) | ![400](capturas/10-error-400-patch.png) |
| Correo duplicado (400) | ![Duplicado](capturas/11-error-400-email.png) |
| Datos invalidos (422) | ![422](capturas/12-error-422.png) |

## 13. Reflexion final sobre la evolucion del proyecto

La diferencia mas grande frente a la version 1.0 no esta en la cantidad de endpoints
sino en la **organizacion**. Al separar `routes`, `services`, `dependencies` y `data`,
cada archivo hace una sola cosa: las rutas solo traducen HTTP, el servicio contiene la
logica y las dependencias concentran las validaciones. Eso hizo que agregar `PUT`,
`PATCH` y `DELETE` fuera casi mecanico.

`Depends()` fue el concepto que mas me sirvio. Antes habria repetido el mismo bloque
"buscar usuario / si no existe lanzar 404" en cuatro endpoints; ahora vive en
`get_user_or_404` y se inyecta donde se necesita. Lo mismo ocurre con la validacion de
correos duplicados y con el control del `PATCH` vacio.

Tambien entendi que los codigos de estado son parte del contrato de la API: un `201`
en el POST, un `400` cuando el cliente manda mal los datos y un `404` cuando el recurso
no existe le dicen al consumidor que paso sin necesidad de leer el mensaje. Unificar el
formato de error con un `exception_handler` completa esa idea, porque el cliente siempre
recibe la misma estructura.

Finalmente, Swagger/OpenAPI dejo de ser "documentacion bonita" para convertirse en la
herramienta con la que probe todos los escenarios, incluidos los de error, sin escribir
un solo cliente HTTP.
