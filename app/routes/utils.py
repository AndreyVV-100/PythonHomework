"""Some testing stuff"""

from typing import Annotated
from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlmodel import Session, select, SQLModel
from app.db import get_session, engine
from app.schemas.schemas import User
from ..logic.auth import get_current_user

router = APIRouter(prefix="/utils", tags=["Вспомогательные инструменты"])

@router.get("/test-db", status_code=status.HTTP_200_OK)
def test_database(session: Session = Depends(get_session)):
    """Database hello world"""
    result = session.exec(select(text("'Hello world'"))).all()
    return result


@router.get("/create-db-tables",
            status_code=status.HTTP_200_OK)
def test_create_database():
    """Create database"""
    SQLModel.metadata.create_all(engine)
    return {"message": "Tables created"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/test-auth")
def show_access_token(token: str = Depends(oauth2_scheme)):
    """Auth in system"""
    return {"token": token}


@router.get("/me", response_model=int,
            summary = 'Получить ID вошедшего пользователя')
def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get user id"""
    return current_user.user_id
