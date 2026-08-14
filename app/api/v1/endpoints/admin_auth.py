"""
Endpoints de autenticación para AdminUsers: login, refresh y logout.
Implementa el modelo híbrido JWT (access, stateless) + refresh token
persistido en BD (stateful) para permitir revocación real de sesiones.
"""
from fastapi import APIRouter, Request, status

from app.api.dependencies import CurrentAdmin, DbSession
from app.core.exceptions import CredentialsException, InvalidRefreshTokenException
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.admin import AdminLoginRequest, RefreshTokenRequest, TokenResponse
from app.services import session_service
from app.services.admin_service import authenticate_admin

router = APIRouter(prefix="/auth", tags=["Admin Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: AdminLoginRequest, request: Request, db: DbSession):
    admin = authenticate_admin(db, payload.email, payload.password)
    if admin is None:
        raise CredentialsException("Email o contraseña incorrectos, o cuenta bloqueada temporalmente")

    access_token = create_access_token(subject=admin.email)
    refresh_token, jti, expires_at = create_refresh_token(subject=admin.email)

    session_service.create_admin_session(
        db, admin_id=admin.id, jti=jti, expires_at=expires_at,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, db: DbSession):
    try:
        claims = decode_token(payload.refresh_token, expected_type="refresh")
    except ValueError as exc:
        raise InvalidRefreshTokenException() from exc

    jti = claims.get("jti")
    email = claims.get("sub")
    session = session_service.get_valid_session_by_jti(db, jti) if jti else None
    if session is None or email is None:
        raise InvalidRefreshTokenException()

    # Rotación de refresh token: se revoca el actual y se emite uno nuevo
    session_service.revoke_session(db, jti)
    new_access_token = create_access_token(subject=email)
    new_refresh_token, new_jti, new_expires_at = create_refresh_token(subject=email)
    session_service.create_admin_session(
        db, admin_id=session.admin_id, jti=new_jti, expires_at=new_expires_at
    )

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshTokenRequest, db: DbSession):
    try:
        claims = decode_token(payload.refresh_token, expected_type="refresh")
    except ValueError as exc:
        raise InvalidRefreshTokenException() from exc

    jti = claims.get("jti")
    if jti:
        session_service.revoke_session(db, jti)


@router.get("/me")
def read_current_admin(current_admin: CurrentAdmin):
    return {
        "id": str(current_admin.id),
        "email": current_admin.email,
        "full_name": current_admin.full_name,
        "is_superadmin": current_admin.is_superadmin,
    }
