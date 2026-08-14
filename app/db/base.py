"""
Punto único de importación de todos los modelos ORM.
Alembic (env.py) importa `Base` desde aquí para autogenerar migraciones,
por eso es obligatorio importar cada modelo nuevo en este archivo aunque
no se use directamente (evita el error 'no changes detected').
"""
from app.db.session import Base  # noqa: F401

from app.models.admin import AdminUser, AdminSession  # noqa: F401
from app.models.tenant import Tenant, TenantUser, TenantSession  # noqa: F401
