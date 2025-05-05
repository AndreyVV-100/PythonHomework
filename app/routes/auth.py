from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from ..schemas import schemas
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..logic import auth as auth
from app.config import settings
from datetime import timedelta
from typing import Annotated, List
from ..logic.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Безопасность"])

@router.post("/signup", status_code=status.HTTP_201_CREATED,
             response_model=int,
             summary = 'Добавить пользователя')
def create_user(user: schemas.User,
                session: Session = Depends(get_session)):
    new_user = schemas.User(
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        workload=user.workload,
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
    statement = (select(schemas.User)
                 .where(schemas.User.email == login_attempt_data.username))
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

@router.get("/me", status_code=status.HTTP_200_OK,
             summary = 'Получить информацию о себе',
             response_model=schemas.User)
def get_me(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    return schemas.User(
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        workload=current_user.workload,
        email=current_user.email,
        password="",
        user_id=current_user.user_id
    )
    
@router.get("/", status_code=status.HTTP_200_OK,
             summary = 'Получить информацию о всех пользователях',
             response_model=List[schemas.User])
def get_users(current_user: Annotated[schemas.User, Depends(get_current_user)],
              session: Session = Depends(get_session)):
    users = session.exec(select(schemas.User)).all()
    new_users = []
    for user in users:
        new_users.append(schemas.User(
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            workload=user.workload,
            email=user.email,
            password="",
            user_id=user.user_id
        ))
    return new_users
