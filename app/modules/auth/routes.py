from fastapi import APIRouter, Depends, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.data_connect import get_db_session as get_db
from app.modules.auth.schema import LoginRequest, MessageResponse
from app.modules.auth.services import AuthService


router = APIRouter(prefix="/admin/auth", tags=["auth"])

@router.post("/login", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user_agent = request.headers.get("user-agent", "unknown")

    await AuthService.login(
        db=db,
        response=response,
        email=payload.email,
        password=payload.password,
        user_agent=user_agent,
    )

    return {"message": "Inicio de sesión exitoso."}

