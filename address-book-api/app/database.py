from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

SQLALCHEMY_DATABASE_URL = "sqlite:///./address_book.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base = declarative_base()

def get_db() -> Generator:
    """
    Provides a transactional database session for a single request/operation.
    The session is closed automatically after the 'yield'.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()