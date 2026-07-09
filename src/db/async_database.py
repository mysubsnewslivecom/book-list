from collections.abc import AsyncGenerator

from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from utils.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_uri

connect_args = {}

if settings.is_sqlite:
    connect_args = {"check_same_thread": False}


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)


async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session() as db:
        try:
            yield db
        finally:
            await db.close()


SQLAlchemyInstrumentor().instrument(
    engine=engine.sync_engine,
)
