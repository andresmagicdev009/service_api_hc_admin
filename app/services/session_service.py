"""
Gestión y revocación de refresh tokens (modelo híbrido: JWT firmado +
registro stateful en BD identificado por 'jti'). Esto permite:
  - Validar la firma/expiración sin ir a BD (parte JWT).
  - Revocar sesiones individualmente o en bloque (parte stateful),
    algo imposible con JWT puramente stateless.
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin import AdminSession


def create_admin_session(
    db: Session, admin_id, jti: str, expires_at: datetime,
    user_agent: str | None = None, ip_address: str | None = None,
) -> AdminSession:
    session = AdminSession(
        admin_id=admin_id, jti=jti, expires_at=expires_at,
        user_agent=user_agent, ip_address=ip_address,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_valid_session_by_jti(db: Session, jti: str) -> AdminSession | None:
    stmt = select(AdminSession).where(
        AdminSession.jti == jti,
        AdminSession.is_revoked.is_(False),
        AdminSession.expires_at > datetime.now(timezone.utc),
    )
    return db.execute(stmt).scalar_one_or_none()


def revoke_session(db: Session, jti: str) -> None:
    stmt = select(AdminSession).where(AdminSession.jti == jti)
    session = db.execute(stmt).scalar_one_or_none()
    if session:
        session.is_revoked = True
        db.commit()


def revoke_all_sessions_for_admin(db: Session, admin_id) -> None:
    """Útil para 'cerrar sesión en todos los dispositivos' o tras cambio de password."""
    stmt = select(AdminSession).where(
        AdminSession.admin_id == admin_id, AdminSession.is_revoked.is_(False)
    )
    for session in db.execute(stmt).scalars():
        session.is_revoked = True
    db.commit()
