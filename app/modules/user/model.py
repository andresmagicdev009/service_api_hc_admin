import enum
import uuid 
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy.orm import relationship
from app.db.base import Base

class TenantStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"
    SUSPENDED = "SUSPENDIDO"
    
    
class UserRoleEnum(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    
class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "admin_schema"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_name = Column(String(150), nullable=False)
    ruc = Column(String(13), nullable=False, unique=True, index=True)
    plan = Column(String(50), nullable=False, default="PRO")
    status = Column(
        SQLEnum(TenantStatusEnum, name="tenant_status_enum", schema="admin_schema"),
        nullable=False,
        default=TenantStatusEnum.ACTIVE
    )
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    users = relationship("User", back_populates="tenant")
    
    
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "admin_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("admin_schema.tenants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(
        SQLEnum(UserRoleEnum, name="user_role_enum", schema="admin_schema"),
        nullable=False,
        default=UserRoleEnum.ADMIN
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant", back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")