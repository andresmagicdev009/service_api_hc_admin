"""DTOs (Pydantic v2) para usuarios finales asociados a un Tenant."""
import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TenantRole(str, Enum):
    ADMIN = "ADMIN"
    MEDICO = "MEDICO"
    FISIOTERAPEUTA = "FISIOTERAPEUTA"
    PASANTE = "PASANTE"
    RECEPCIONISTA = "RECEPCIONISTA"
    PACIENTE = "PACIENTE"


class TenantUserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    role: TenantRole


class TenantUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: EmailStr
    full_name: str
    role: TenantRole
    is_active: bool
    created_at: datetime
