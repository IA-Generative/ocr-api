# conftest.py
import multiprocessing

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.connector.db_connector import Base

multiprocessing.set_start_method("spawn", force=True)


# Base de données SQLite async pour les tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_engine():
    """Crée un moteur de base de données async pour les tests"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"timeout": 30},
    )

    # Créer les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Nettoyer après les tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session_maker(async_engine):
    """Crée une factory de session async"""
    async_session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    return async_session_factory


@pytest_asyncio.fixture
async def db_session(async_session_maker):
    """Crée une session de base de données pour chaque test"""
    async with async_session_maker() as session:
        yield session
