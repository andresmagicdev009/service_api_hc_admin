"""
Lógica de negocio para autenticación y gestión de AdminUsers.
Incluye bloqueo de cuenta por intentos fallidos (account lockout).
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.admin import AdminUser
from app.schemas.admin import AdminCreate

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


def get_admin_by_email(db: Session, email: str) -> AdminUser | None:
    stmt = select(AdminUser).where(AdminUser.email == email)
    return db.execute(stmt).scalar_one_or_none()


def create_admin(db: Session, data: AdminCreate) -> AdminUser:
    admin = AdminUser(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        is_superadmin=data.is_superadmin,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def authenticate_admin(db: Session, email: str, password: str) -> AdminUser | None:
    """
    Retorna el AdminUser si las credenciales son válidas y la cuenta no está
    bloqueada; None en caso contrario. Actualiza el contador de intentos fallidos.
    """
    admin = get_admin_by_email(db, email)
    if admin is None:
        return None

    if admin.locked_until and admin.locked_until > datetime.now(timezone.utc):
        return None  # Cuenta temporalmente bloqueada

    if not verify_password(password, admin.hashed_password):
        admin.failed_login_attempts += 1
        if admin.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            admin.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        db.commit()
        return None

    # Login exitoso: resetear contador de intentos fallidos
    admin.failed_login_attempts = 0
    admin.locked_until = None
    db.commit()
    return admin
