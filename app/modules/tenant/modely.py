import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.shared.enums.tenant_enum import TenantStatusEnum, ServiceTypeEnum
class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "admin_schema"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_name: Mapped[str] = mapped_column(String(150), nullable=False)
    
    # RUC de 13 dígitos (Ecuador)
    ruc: Mapped[str] = mapped_column(String(13), nullable=False, unique=True, index=True)
    
    # Nombre único del esquema PostgreSQL (ej: "tenant_empresa_a")
    schema_name: Mapped[str] = mapped_column(String(63), nullable=False, unique=True)
    
    # Tipo de esquema/servicio asignado (ERP o CRM)
    service_type: Mapped[ServiceTypeEnum] = mapped_column(
        SQLEnum(ServiceTypeEnum, name="service_type_enum", schema="admin_schema"),
        nullable=False,
        default=ServiceTypeEnum.ERP
    )
    
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="PRO")
    
    status: Mapped[TenantStatusEnum] = mapped_column(
        SQLEnum(TenantStatusEnum, name="tenant_status_enum", schema="admin_schema"),
        nullable=False,
        default=TenantStatusEnum.SUSPENDED
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relación hacia los usuarios
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")