"""
Configuración global de la aplicación usando Pydantic Settings.
Lee variables desde el entorno / archivo .env
"""
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # --- App ---
    PROJECT_NAME: str = "Admin Core API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # --- Database ---
    DATABASE_URL: str

    # --- Seguridad ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FERNET_KEY: str  # Usado para cifrar URIs de conexión de tenants (Db_medic)

    # --- CORS ---
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v


settings = Settings()
