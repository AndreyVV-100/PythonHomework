from app.config import settings as cnf
from sqlmodel import create_engine, Session, SQLModel

DB_URL = f"postgresql://{cnf.db_username}:{cnf.db_password}@{cnf.db_host}:{cnf.db_port}/{cnf.db_name}"
engine = create_engine(DB_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_database():
    SQLModel.metadata.create_all(engine)
