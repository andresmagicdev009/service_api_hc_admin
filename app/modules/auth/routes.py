from fastapi import APIRouter, Depends, status, Request, Response
from sqlalchemy.orm import Session
from app.db.data_connect import get_db_session as get_db
from app.modules.auth.schema import LoginRequest, MessageResponse
from app.modules.auth.services import AuthService


router = APIRouter(prefix="/api/v1/admin/auth", tags=["auth"])

@router.post("/login", status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user_agent = request.headers.get("user-agent", "unknown")
    
    user = AuthService.login(
        db = db,
        response = response,
        email = payload.email,
        password = payload.password,
        user_agent = user_agent
    )
    
    return {"message" : "Inicio de sesión exitoso."}

