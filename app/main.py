"""
Punto de entrada de la aplicación FastAPI: instancia la app, configura
middlewares (CORS) y registra el router principal de la API v1.
"""
from app.core.logger import logger
from alembic.util import status
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.middleware import ClientIPMiddleware
from app.db import data_connect as connection_to_db



app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check(db: AsyncSession = Depends(connection_to_db.get_db_session)):
    try:
        # Se ejecuta una consula rapida sobre la sesion actual 
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            return {
                "status": "healthy",
                "database": "connected"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "unhealthy", "database": "unexpected response"}
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "database": str(e)}
        )  
        
        
# Registro del middleware para capturar la IP del cliente
app.add_middleware(ClientIPMiddleware)

@app.get("/hello-world")
async def get_users():
    logger.info("Consulta de datos de inventario")
    return {"message": "Success"}
