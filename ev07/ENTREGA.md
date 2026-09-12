# Entrega EV07 — Fundamentos de FastAPI (API REST de Usuarios)

**Guia:** GA1-220501096-01-AA1-EV07 · **Duracion:** 9 horas
**Proyecto:** [`device_systems/`](device_systems/) · **README:** [device_systems/README.md](device_systems/README.md)

## Checklist de evidencias

| # | Evidencia pedida | Donde esta | Estado |
|---|---|---|---|
| 1 | Proyecto `device_systems` funcional | `ev07/device_systems/` | Listo |
| 2 | Recurso `users` implementado | `app/routes/user_routes.py` | Listo |
| 3 | Endpoints GET | `GET /users`, `GET /users/{user_id}`, `?role=`, `?is_active=` | Listo |
| 4 | Endpoint POST | `POST /users` con `201 Created` | Listo |
| 5 | Validaciones con Pydantic v2 | `app/schemas/user_schema.py` | Listo |
| 6 | Response Models | `UserResponse`, `UserListResponse` | Listo |
| 7 | Cabeceras HTTP personalizadas | Middleware en `app/main.py` (`X-App-Name`, `X-API-Version`) | Listo |
| 8 | README.md documentado | `device_systems/README.md` | Listo |
| 9 | Capturas de Swagger UI y pruebas | `evidencia/capturas/` + `evidencia/EVIDENCIA.md` | Listo |

## Como ejecutar el proyecto

1. Levantar el servidor:

```bash
cd ev07/device_systems
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Abrir http://127.0.0.1:8000/docs. Las 8 capturas de evidencia ya estan
   generadas en `evidencia/capturas/` y documentadas en `evidencia/EVIDENCIA.md`.

## Guion para la socializacion (5 minutos)

1. **Como organice el proyecto:** carpetas `app/schemas` (modelos) y `app/routes`
   (endpoints), con `main.py` como punto de entrada.
2. **Como implemente el recurso users:** lista en memoria + funciones auxiliares
   (`siguiente_id`, `email_registrado`).
3. **Como aplique Pydantic:** `UserCreate` valida la entrada (nombre minimo 3,
   `EmailStr`, rol con `Enum`) y `UserResponse` controla la salida.
4. **Como funcionan GET y POST:** path parameter `user_id`, query parameters
   `role` e `is_active`, y POST que devuelve `201` y evita correos duplicados.
5. **Que aprendi:** FastAPI valida y documenta solo; Swagger UI sirve para probar.
