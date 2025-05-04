from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from ..schemas import schemas as schema_task
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..logic import auth as auth
from app.config import settings
from datetime import timedelta


router = APIRouter(prefix="/auth", tags=["Безопасность"])

@router.post("/signup", status_code=status.HTTP_201_CREATED,
             response_model=int,
             summary = 'Добавить пользователя')
def create_user(user: schema_task.User,
                session: Session = Depends(get_session)):
    new_user = schema_task.User(
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        email=user.email,
        password=auth.get_password_hash(user.password)
    )
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user.user_id
    except IntegrityError as e:
        assert isinstance(e.orig, UniqueViolation)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"User with email {user.email} already exists"
        )


@router.post("/login", status_code=status.HTTP_200_OK,
             summary = 'Войти в систему')
def user_login(login_attempt_data: OAuth2PasswordRequestForm = Depends(),
               db_session: Session = Depends(get_session)):
    statement = (select(schema_task.User)
                 .where(schema_task.User.email == login_attempt_data.username))
    existing_user = db_session.exec(statement).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {login_attempt_data.username} not found"
        )

    if auth.verify_password(
            login_attempt_data.password,
            existing_user.password):
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth.create_access_token(
            data={"sub": login_attempt_data.username},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong password for user {login_attempt_data.username}"
        )
