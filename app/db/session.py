import os
import psycopg
import asyncio
import sys

from sqlalchemy import text
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
#from app.core.config import settings
from dotenv import load_dotenv


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


#Load environment variables from .env file
load_dotenv()

## Load environment variables from .env file
url_database_string = os.getenv("DATABASE_URL")


# Uso del drives asincrono 
if url_database_string and url_database_string.startswith("postgresql://"):
    url_database_string = url_database_string.replace("postgresql://", "postgresql+psycopg://",1)
    
# Database engine connection 
engine = create_async_engine(
    url_database_string,
    echo = True, # Para ver consultas SQL en la consola
    future=True,
    pool_pre_ping = True,
)    

# Async connection factory
AsyncSessionLocal = async_sessionmaker(
    bind = engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Funcion para obtener la sesion ideal para FastAPI
async def get_db_session()->AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            
 
 
# Funcion para testear la conexion a la base de datos           
async def test_db_connection() -> bool:
    """
    Intenta ejecutar una consulta simple para verificar la conexión con Neon.
    Devuelve True si la conexión es exitosa, o False si falla.
    """
    
    try:
        async with engine.connect() as connection:
            # Ejecutamos una consulta rápida y liviana
            result = await connection.execute(text("SELECT 1"))
            value = result.scalar()
            db_name = engine.url.database or "Unkwnow DATABASE!@"
            
            if value == 1:
                print(f" Conexión exitosa a la base de datos de Neon." "Base de datos", {db_name})
                return True
            else:
                print(" La consulta de prueba no devolvió el valor esperado.")
                return False

    except Exception as e:
        print(f" Error al conectar a la base de datos: {e}")
        return False
    
    
# Bloque temporal eliminar este bloque y la funcion de prueba de conexion en produccion

if __name__ == "__main__":
    #Permite ejecutar: session.py
    asyncio.run(test_db_connection())