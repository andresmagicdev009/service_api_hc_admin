from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencies import get_current_user, oauth2_scheme, db_users
from app.core.security import create_access_token, verify_password
from app.modules.auth.schema import Token

from app.modules.auth.session import active_sessions  # Importación corregida

router = APIRouter()

