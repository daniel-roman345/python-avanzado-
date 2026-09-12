# Entrega EV08 — FastAPI Intermedio (CRUD, errores, Swagger y Depends)

**Guia:** GA1-220501096-01-AA1-EV08 · **Duracion:** 12 horas
**Proyecto:** [`device_systems/`](device_systems/) · **README:** [device_systems/README.md](device_systems/README.md)

## Checklist de evidencias

| # | Evidencia pedida | Donde esta | Estado |
|---|---|---|---|
| 1 | Proyecto `device_systems` actualizado | `ev08/device_systems/` | Listo |
| 2 | Estructura por capas (routes, schemas, services, dependencies, data) | `app/` | Listo |
| 3 | `PUT /users/{user_id}` (200 / 404) | `app/routes/user_routes.py` | Listo |
| 4 | `PATCH /users/{user_id}` (200 / 400 si viene vacio) | `app/routes/user_routes.py` | Listo |
| 5 | `DELETE /users/{user_id}` (200 con mensaje / 404) | `app/routes/user_routes.py` | Listo |
| 6 | Codigos de estado HTTP correctos | Tabla en el README, seccion 6 | Listo |
| 7 | Manejo de errores con `HTTPException` + respuesta estructurada | `app/main.py` y `app/dependencies/` | Listo |
| 8 | Dependency Injection con `Depends()` | `app/dependencies/user_dependencies.py` | Listo |
| 9 | Documentacion Swagger/OpenAPI mejorada (tags, summary, description) | `app/main.py` y rutas | Listo |
| 10 | README.md completo | `device_systems/README.md` | Listo |
| 11 | Capturas de Swagger UI y ReDoc + pruebas de cada endpoint y de errores | `evidencia/capturas/` | Listo |

## Como ejecutar el proyecto

```bash
cd ev08/device_systems
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Las 12 capturas de evidencia ya estan en `evidencia/capturas/` (incluye `/docs`,
`/redoc`, los 6 metodos y los 4 escenarios de error) y se explican en
`evidencia/EVIDENCIA.md`.

## Guion para la socializacion (5 minutos)

1. **Cambios frente a la version anterior:** separacion en capas y CRUD completo.
2. **PUT vs PATCH:** `UserUpdate` exige todos los campos; `UserPatch` usa campos
   opcionales y `model_dump(exclude_unset=True)`; si no llega nada → `400`.
3. **DELETE:** elimina y responde `200` con mensaje; si no existe → `404`.
4. **Errores con HTTPException:** un `exception_handler` unifica el formato
   `{error, message, status_code, path}`.
5. **Codigos HTTP:** `201` al crear, `400` por datos duplicados o PATCH vacio,
   `404` cuando no existe, `422` cuando Pydantic rechaza los datos.
6. **Depends():** `get_user_or_404` se escribe una vez y la usan 4 endpoints.
7. **Swagger/OpenAPI:** permite probar todos los escenarios sin cliente externo.
