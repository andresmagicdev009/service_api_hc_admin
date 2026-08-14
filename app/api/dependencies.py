"""
Dependencias reutilizables de FastAPI: obtención de sesión de BD y
verificación del AdminUser autenticado a partir del access token JWT.
"""
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import CredentialsException, InactiveUserException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.admin import AdminUser
from app.services.admin_service import get_admin_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/auth/login")

DbSession = Annotated[Session, Depends(get_db)]


def get_current_admin(
    db: DbSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> AdminUser:
    try:
        payload = decode_token(token, expected_type="access")
    except ValueError as exc:
        raise CredentialsException() from exc

    email: str | None = payload.get("sub")
    if email is None:
        raise CredentialsException()

    admin = get_admin_by_email(db, email)
    if admin is None:
        raise CredentialsException()
    if not admin.is_active:
        raise InactiveUserException()

    return admin


CurrentAdmin = Annotated[AdminUser, Depends(get_current_admin)]


def require_superadmin(admin: CurrentAdmin) -> AdminUser:
    """Dependencia adicional para endpoints reservados a superadmins (RBAC simple)."""
    if not admin.is_superadmin:
        raise InactiveUserException(detail="Se requieren privilegios de superadmin")
    return admin


SuperAdmin = Annotated[AdminUser, Depends(require_superadmin)]
