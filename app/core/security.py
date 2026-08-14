"""
Utilidades de seguridad:
- Hash de contraseñas con Argon2
- Cifrado simétrico (Fernet/AES) para URIs de conexión de tenants
- Creación y verificación de JWT (access + refresh)
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt

from app.core.config import settings

# --- Hash de contraseñas (Argon2id, recomendado por OWASP sobre bcrypt) ---
_pwd_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
    return _pwd_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _pwd_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


# --- Cifrado simétrico para datos sensibles (ej. connection string de tenant DB) ---
_fernet = Fernet(settings.FERNET_KEY.encode())


def encrypt_value(raw_value: str) -> str:
    return _fernet.encrypt(raw_value.encode()).decode()


def decrypt_value(encrypted_value: str) -> str:
    try:
        return _fernet.decrypt(encrypted_value.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("No se pudo desencriptar el valor: token inválido") from exc


# --- JWT: access token (stateless) + refresh token (stateful, se guarda hash en BD) ---
TokenType = Literal["access", "refresh"]


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "type": "access", "exp": expire, "iat": datetime.now(timezone.utc)}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    """
    Devuelve (token_jwt, jti, expires_at).
    El jti (JWT ID) es lo que se persiste en la tabla de sesiones para poder
    revocar el token individualmente (modelo híbrido stateful).
    """
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "type": "refresh",
        "jti": jti,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, expire


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Token inválido o expirado") from exc

    if expected_type and payload.get("type") != expected_type:
        raise ValueError(f"Se esperaba un token de tipo '{expected_type}'")
    return payload
