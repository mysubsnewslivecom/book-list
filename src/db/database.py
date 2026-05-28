from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from utils.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_uri

connect_args = {}

if settings.is_sqlite:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
