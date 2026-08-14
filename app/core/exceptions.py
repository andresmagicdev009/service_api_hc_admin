"""
Excepciones personalizadas del dominio.
"""
from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(self, detail: str = "No se pudieron validar las credenciales"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserException(HTTPException):
    def __init__(self, detail: str = "El usuario se encuentra inactivo"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class TenantNotFoundException(HTTPException):
    def __init__(self, tenant_id: str | None = None):
        detail = f"Tenant '{tenant_id}' no encontrado" if tenant_id else "Tenant no encontrado"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class TenantAlreadyExistsException(HTTPException):
    def __init__(self, identifier: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un tenant con el identificador '{identifier}'",
        )


class InvalidRefreshTokenException(HTTPException):
    def __init__(self, detail: str = "Refresh token inválido, expirado o revocado"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
