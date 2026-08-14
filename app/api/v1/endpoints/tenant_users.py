"""
Gestión de usuarios finales asociados a un Tenant (registro liviano a nivel
de Core API; el detalle clínico de cada usuario vive en la BD del tenant).
"""
import uuid

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.dependencies import CurrentAdmin, DbSession
from app.core.exceptions import TenantNotFoundException
from app.models.tenant import TenantUser
from app.schemas.user import TenantUserCreate, TenantUserResponse
from app.services.tenant_service import get_tenant_or_404

router = APIRouter(prefix="/tenants/{tenant_id}/users", tags=["Tenant Users"])


@router.post("", response_model=TenantUserResponse, status_code=status.HTTP_201_CREATED)
def create_tenant_user(tenant_id: uuid.UUID, payload: TenantUserCreate, db: DbSession, _: CurrentAdmin):
    get_tenant_or_404(db, tenant_id)  # valida existencia del tenant

    user = TenantUser(tenant_id=tenant_id, **payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[TenantUserResponse])
def list_tenant_users(tenant_id: uuid.UUID, db: DbSession, _: CurrentAdmin):
    get_tenant_or_404(db, tenant_id)
    stmt = select(TenantUser).where(TenantUser.tenant_id == tenant_id)
    return list(db.execute(stmt).scalars())
