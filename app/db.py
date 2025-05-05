"""Module for database initialization and working"""

from sqlmodel import create_engine, Session, SQLModel
from app.config import settings as cnf

DB_URL = f"postgresql://{cnf.db_username}:{cnf.db_password}" \
         f"@{cnf.db_host}:{cnf.db_port}/{cnf.db_name}"
engine = create_engine(DB_URL, echo=True)

def get_session():
    """Return current database session"""
    with Session(engine) as session:
        yield session

def init_database():
    """Initialize database"""
    SQLModel.metadata.create_all(engine)
