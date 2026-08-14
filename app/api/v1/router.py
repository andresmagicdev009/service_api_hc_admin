"""Agregador de rutas de la versión 1 de la API."""
from fastapi import APIRouter

from app.api.v1.endpoints import admin_auth, tenant_users, tenants

api_router = APIRouter()
api_router.include_router(admin_auth.router, prefix="/admin")
api_router.include_router(tenants.router)
api_router.include_router(tenant_users.router)
