"""
Engine y Session de SQLAlchemy 2.0 para la base de datos CORE
(la que almacena Admins y el registro de Tenants).
Cada Tenant tiene su propia base de datos física (Db_medic), cuya conexión
se resuelve dinámicamente en tenant_service.py usando la URI cifrada.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

_engine_kwargs = {"pool_pre_ping": True}
if not settings.DATABASE_URL.startswith("sqlite"):
    # SQLite (usado en tests) no soporta pool_size/max_overflow (QueuePool)
    _engine_kwargs.update(pool_size=10, max_overflow=20)

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
