"""
Modelos ORM relacionados con Tenants (clínicas/organizaciones cliente) y sus
usuarios finales. La conexión física de cada Tenant a su propia base de datos
(Db_medic) se resuelve vía `encrypted_db_uri`, desencriptada en runtime.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    # URI de conexión a la BD física del tenant, cifrada con Fernet (ver core/security.py)
    db_uri: Mapped[str] = mapped_column(Text, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    provisioned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    users: Mapped[list["TenantUser"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )


class TenantUser(Base):
    """
    Referencia liviana, a nivel de Core API, de qué usuarios pertenecen a qué
    tenant (útil para login federado / resolución de tenant antes de conectar
    a la BD física). Los datos clínicos completos viven en la BD del tenant.
    """
    __tablename__ = "tenant_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))

    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # ADMIN, MEDICO, RECEPCIONISTA, etc.

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tenant: Mapped["Tenant"] = relationship(back_populates="users")


class TenantSession(Base):
    """Sesiones (refresh tokens) de usuarios finales de un tenant."""
    __tablename__ = "tenant_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenant_users.id", ondelete="CASCADE"))
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)

    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
