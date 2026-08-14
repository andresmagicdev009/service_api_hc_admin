"""
CRUD de Tenants. Solo accesible por administradores autenticados
(y en operaciones sensibles, exclusivamente por superadmins).
"""
import uuid

from fastapi import APIRouter, status

from app.api.dependencies import CurrentAdmin, DbSession, SuperAdmin
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.services import tenant_service

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(payload: TenantCreate, db: DbSession, _: SuperAdmin):
    tenant = tenant_service.create_tenant(db, payload)
    return tenant


@router.get("", response_model=list[TenantResponse])
def list_tenants(db: DbSession, _: CurrentAdmin, skip: int = 0, limit: int = 50):
    return tenant_service.list_tenants(db, skip=skip, limit=limit)


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: uuid.UUID, db: DbSession, _: CurrentAdmin):
    return tenant_service.get_tenant_or_404(db, tenant_id)


@router.patch("/{tenant_id}", response_model=TenantResponse)
def update_tenant(tenant_id: uuid.UUID, payload: TenantUpdate, db: DbSession, _: SuperAdmin):
    return tenant_service.update_tenant(db, tenant_id, payload)
