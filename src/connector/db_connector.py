import os
from contextlib import contextmanager
from datetime import datetime

import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from src.schemas.health import Health

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./example.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()
Session = scoped_session(SessionLocal)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_db = contextmanager(get_session)
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
        return Health(name="db", version=sqlalchemy.__version__, up_time=self.up_time, status="healthy")


db_client_connector = DbConnector()

