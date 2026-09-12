# Evidencias EV08 — FastAPI Intermedio (CRUD, errores, Swagger y Depends)

**Guia:** GA1-220501096-01-AA1-EV08
**Aprendiz:** Daniel Roman
**Proyecto:** `device_systems` (v2.0.0) — codigo en `../device_systems/`
**Repositorio:** https://github.com/daniel-roman345/python-avanzado-

---

## 1. Documentacion automatica

### 1.1 Swagger UI (`/docs`)

Endpoints organizados con los tags **Users** y **Root**, cada uno con `summary`,
`description` y los codigos de respuesta posibles.

![Swagger UI](capturas/01-swagger-ui.png)

### 1.2 ReDoc (`/redoc`)

![ReDoc](capturas/02-redoc.png)

## 2. Evidencia de pruebas de cada endpoint

### 2.1 `GET /users`

![GET /users](capturas/03-get-users.png)

### 2.2 `GET /users/{user_id}`

![GET /users/2](capturas/04-get-user-id.png)

### 2.3 `POST /users` — `201 Created`

![POST /users](capturas/05-post-users.png)

### 2.4 `PUT /users/{user_id}` — actualizacion completa, `200 OK`

![PUT](capturas/06-put-user.png)

### 2.5 `PATCH /users/{user_id}` — actualizacion parcial, `200 OK`

Solo se envio `{"role": "support"}` y el resto de los campos se conservo.

![PATCH](capturas/07-patch-user.png)

### 2.6 `DELETE /users/{user_id}` — `200 OK` con mensaje

![DELETE](capturas/08-delete-user.png)

## 3. Evidencia de errores controlados

### 3.1 Usuario no encontrado — `404`

![404](capturas/09-error-404.png)

### 3.2 PATCH sin datos — `400`

![400 patch](capturas/10-error-400-patch.png)

### 3.3 Correo duplicado — `400`

![400 email](capturas/11-error-400-email.png)

### 3.4 Datos invalidos — `422`

![422](capturas/12-error-422.png)

Todas las respuestas de error usan el mismo formato gracias al `exception_handler`
registrado en `app/main.py`:

```json
{ "error": true, "message": "Usuario no encontrado", "status_code": 404, "path": "/users/99" }
```

## 4. Explicacion de la estructura del proyecto

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| Rutas | `app/routes/` | Definen endpoints y codigos HTTP; no contienen logica de negocio |
| Schemas | `app/schemas/` | Modelos Pydantic de entrada (`UserCreate`, `UserUpdate`, `UserPatch`) y salida (`UserResponse`) |
| Servicios | `app/services/` | Logica de negocio pura, sin FastAPI |
| Dependencias | `app/dependencies/` | Validaciones y busquedas reutilizables inyectadas con `Depends()` |
| Datos | `app/data/` | Base de datos simulada en memoria |

Separar estas capas permitio agregar `PUT`, `PATCH` y `DELETE` sin tocar la logica ya
existente y mantener cada archivo con una sola responsabilidad.

## 5. Como se aplico Dependency Injection

| Dependencia | Que hace | Donde se usa |
|---|---|---|
| `get_user_or_404` | Busca el usuario y lanza `404` si no existe | `GET`, `PUT`, `PATCH`, `DELETE` por ID |
| `validar_email_unico` | Impide crear correos duplicados | `POST /users` |
| `validar_email_unico_en_actualizacion` | Impide que un `PUT` repita el correo de otro usuario | `PUT /users/{id}` |
| `validar_patch_no_vacio` | Devuelve `400` si el `PATCH` llega vacio | `PATCH /users/{id}` |
| `validar_rol_permitido` | Valida el rol del query parameter | `GET /users` |
| `get_api_settings` | Entrega la configuracion general | `GET /` |
| `verificar_api_key` | Autenticacion basica simulada por cabecera | disponible para proteger rutas |

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

La busqueda y el `404` se escriben una sola vez y cuatro endpoints los reutilizan.

## 6. Resumen de pruebas

| # | Prueba | Esperado | Resultado |
|---|---|---|---|
| 1 | `GET /users` | `200` | OK |
| 2 | `GET /users/2` | `200` | OK |
| 3 | `GET /users/99` | `404` | OK |
| 4 | `POST /users` | `201` | OK |
| 5 | `POST` correo repetido | `400` | OK |
| 6 | `POST` datos invalidos | `422` | OK |
| 7 | `PUT /users/2` | `200` | OK |
| 8 | `PUT /users/99` | `404` | OK |
| 9 | `PATCH /users/3` | `200` | OK |
| 10 | `PATCH` vacio | `400` | OK |
| 11 | `DELETE /users/4` | `200` | OK |
| 12 | `DELETE` repetido | `404` | OK |

## 7. Reflexion final sobre la evolucion del proyecto

La diferencia mas grande frente a la version 1.0 no esta en la cantidad de endpoints
sino en la organizacion. Al separar `routes`, `services`, `dependencies` y `data`, cada
archivo hace una sola cosa y agregar los nuevos metodos fue casi mecanico.

`Depends()` fue el concepto que mas me sirvio: antes habria repetido el bloque
"buscar usuario / si no existe lanzar 404" en cuatro endpoints; ahora vive en una sola
funcion. Lo mismo con la validacion de correos y el control del `PATCH` vacio.

Tambien entendi que los codigos de estado son parte del contrato de la API: un `201` al
crear, un `400` cuando el cliente envia mal los datos y un `404` cuando el recurso no
existe comunican el resultado sin necesidad de leer el mensaje. Unificar el formato de
error con un `exception_handler` completa esa idea, porque el cliente siempre recibe la
misma estructura.
