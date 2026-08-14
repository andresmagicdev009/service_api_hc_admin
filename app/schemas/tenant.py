"""DTOs (Pydantic v2) para gestión de Tenants."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    # URI en texto plano al crear; el service la cifra antes de persistir
    db_uri: str = Field(min_length=10)

    @field_validator("slug")
    @classmethod
    def slug_lowercase(cls, v: str) -> str:
        return v.lower()


class TenantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    is_active: bool | None = None


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    is_active: bool
    provisioned_at: datetime | None
    created_at: datetime
