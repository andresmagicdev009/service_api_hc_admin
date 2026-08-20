"""Agregador de rutas de la versión 1 de la API."""
from fastapi import APIRouter

from app.modules.auth.routes import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router)


