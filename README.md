# Admin Core API

Plantilla base para una API de administración multi-tenant construida con
**FastAPI + SQLAlchemy 2.0 + PostgreSQL**, siguiendo una arquitectura por capas
(API → Services → Models/DB) inspirada en principios de Clean Architecture.

## Arquitectura

```
Cliente HTTP
    │
    ▼
app/api/           → Controladores (routers), validación de entrada, auth
    │
    ▼
app/services/       → Lógica de negocio (casos de uso), independiente de HTTP
    │
    ▼
app/models/ + db/   → Persistencia (SQLAlchemy ORM)
```

- **`app/api`**: capa de entrada HTTP. Los endpoints son delgados: validan con
  Pydantic (`schemas`), delegan la lógica a `services` y devuelven DTOs.
- **`app/core`**: configuración (`config.py`), seguridad (`security.py`:
  Argon2 + Fernet + JWT) y excepciones de dominio.
- **`app/services`**: lógica de negocio pura, testeable sin FastAPI.
- **`app/models`**: entidades ORM. `Tenant` guarda su URI de conexión
  **cifrada** (Fernet/AES) para permitir provisionamiento dinámico de bases
  de datos físicas por tenant (`Db_medic`).
- **Autenticación híbrida**: access token JWT stateless (`ACCESS_TOKEN_EXPIRE_MINUTES`)
  + refresh token stateful persistido en BD por `jti`, con rotación en cada
  refresh y revocación real (logout, lockout, "cerrar sesión en todos lados").

## Puesta en marcha

```bash
cp .env.example .env
# Genera y coloca tus propios secretos:
openssl rand -hex 32                                                    # JWT_SECRET_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # FERNET_KEY

docker compose up --build
```

La API queda disponible en `http://localhost:8000`, con documentación
interactiva en `http://localhost:8000/docs`.

### Migraciones

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

### Tests

```bash
pip install -r requirements.txt
pytest -v
```

## Próximos pasos sugeridos

- [ ] Implementar RBAC granular por rol de `TenantUser` (decorador o dependencia por permiso).
- [ ] Middleware de resolución de tenant (subdominio o header `X-Tenant-Slug`) para enrutar dinámicamente a la BD física correspondiente.
- [ ] Rate limiting en `/admin/auth/login` para mitigar fuerza bruta a nivel de red (además del lockout a nivel de aplicación).
- [ ] Logging estructurado (structlog) y correlación de requests (request id).
- [ ] CI (GitHub Actions): lint (ruff), tests, build de imagen Docker.
