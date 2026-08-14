"""
Lógica de negocio para creación y gestión de Tenants, incluyendo el
cifrado de la URI de conexión a su base de datos física (Db_medic).
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import TenantAlreadyExistsException, TenantNotFoundException
from app.core.security import decrypt_value, encrypt_value
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


def get_tenant_by_slug(db: Session, slug: str) -> Tenant | None:
    stmt = select(Tenant).where(Tenant.slug == slug)
    return db.execute(stmt).scalar_one_or_none()


def create_tenant(db: Session, data: TenantCreate) -> Tenant:
    if get_tenant_by_slug(db, data.slug) is not None:
        raise TenantAlreadyExistsException(data.slug)

    tenant = Tenant(
        name=data.name,
        slug=data.slug,
        encrypted_db_uri=encrypt_value(data.db_uri),
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    # TODO: disparar aquí el provisionamiento real (crear BD física,
    # correr migraciones iniciales) y luego marcar provisioned_at.
    tenant.provisioned_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(tenant)
    return tenant


def get_tenant_or_404(db: Session, tenant_id) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise TenantNotFoundException(str(tenant_id))
    return tenant


def update_tenant(db: Session, tenant_id, data: TenantUpdate) -> Tenant:
    tenant = get_tenant_or_404(db, tenant_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    db.commit()
    db.refresh(tenant)
    return tenant


def get_decrypted_db_uri(tenant: Tenant) -> str:
    """Usado por la capa de infraestructura para abrir conexión a la BD del tenant."""
    return decrypt_value(tenant.encrypted_db_uri)


def list_tenants(db: Session, skip: int = 0, limit: int = 50) -> list[Tenant]:
    stmt = select(Tenant).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars())
