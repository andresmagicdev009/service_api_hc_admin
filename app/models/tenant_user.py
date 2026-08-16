import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.enums import tenant_user_role

if TYPE_CHECKING:
    from app.models.user import User

class TenantUser(Base):
    __tablename__ = "tenant_users"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="unique_tenant_user"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[tenant_user_role.TenantUserRoles] = mapped_column(Enum(tenant_user_role.TenantUserRoles), default=tenant_user_role.TenantUserRoles.MEMBER, nullable=False)

    user: Mapped["User"] = relationship(back_populates="tenants")