import os 
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.db.data_connect import get_db_session as get_db
from app.modules.auth.model import UserSession
from app.modules.user.model import User, UserRoleEnum
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.modules.auth.session import active_sessions

SECRET_KEY = os.getenv("SECRET_KEY", "dev_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales no válidas o sesión expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verificación de ESTADO de la sesión
    if token not in active_sessions:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None or active_sessions.get(token) != username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user

# Atajos de dependencias para los endpoints
