
import sys
import os 

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response, HTTPException, status
from app.modules.user.model import User
from app.modules.auth.model import UserSession
from app.modules.user.service import PWD_CONTEXT
from app.core.context import client_ip_ctx
from dotenv import load_dotenv
from app.core.config import settings


load_dotenv()


class AuthService:
    @staticmethod
    async def login(db: AsyncSession, response: Response, email: str, password: str, user_agent: str):
        ip_address = client_ip_ctx.get()  # Obtener la IP del cliente desde el contexto
        
        #1 Buscar el usuario y validar que este activo 
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
       
       # 2. Validar credenciales si no existe o la contra no coinciden
        if not user or not PWD_CONTEXT.verify(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas."
            )
        
        # 3. Validar que el usuario se encuentre activo 
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario se encuentra inactivo. Contacte con soporte."
            )

        #4 Generar el token con jti
        jti = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
       
        token_payload = {
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "role": user.role.value,
            "jti": jti,
            "exp": expires_at,
        }
       
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
       
       #5. Registrar sesion activa en BD (admin_schema.user_sessions)
        session = UserSession(
            user_id=user.id,
            jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            is_revoked=False,
            expires_at=expires_at,
        )
       
        db.add(session)
        await db.commit()
       
       #6. Asignar Cookie HttpOnly 
        response.set_cookie(
            key="access_token",
            value=f"Bearer {token}",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )
        return user
   
   
   #Aqui va la funcion para desloguearse
       