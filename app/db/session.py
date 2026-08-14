from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings


database_url = settings.DATABASE_URL
if database_url.startswith('postgresql://')


