import os
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime

import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from src.schemas.health import Health

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./example.db")

# Configuration synchrone
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()
Session = scoped_session(SessionLocal)


# Configuration asynchrone
SQLALCHEMY_ASYNC_DATABASE_URL = os.environ.get("DATABASE_ASYNC_URL", "sqlite+aiosqlite:///./example.db")
async_engine = create_async_engine(
    SQLALCHEMY_ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"timeout": 30},
)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_db = contextmanager(get_session)


@asynccontextmanager
async def get_async_session():
    """Async context manager pour les sessions asynchrones"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


get_async_db = asynccontextmanager(get_async_session)


class DbConnector:
    def __init__(self):
        self.up_time = datetime.now().isoformat()

    def get_health(self):
        try:
            with SessionLocal() as session:
                session.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            return Health(
                name="db",
                extras={"error": str(e)},
                version=sqlalchemy.__version__,
                up_time=self.up_time,
                status="unhealthy",
            )
        return Health(
            name="db",
            version=sqlalchemy.__version__,
            up_time=self.up_time,
            status="healthy",
        )

    async def aget_health(self):
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            return Health(
                name="db",
                extras={"error": str(e)},
                version=sqlalchemy.__version__,
                up_time=self.up_time,
                status="unhealthy",
            )
        return Health(
            name="db",
            version=sqlalchemy.__version__,
            up_time=self.up_time,
            status="healthy",
        )


db_client_connector = DbConnector()
