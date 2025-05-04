from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from app.config import settings
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session, select
from app.db import get_session
from app.schemas import schemas as schema_task

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict,
                        expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = (datetime.now(timezone.utc) +
                  expires_delta)
    else:
        expire = (datetime.now(timezone.utc) +
                  timedelta(minutes=15))

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode,
                             settings.secret_key,
                             algorithm=settings.algo)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                     db_session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algo])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    statement = (select(schema_task.User)
                 .where(schema_task.User.email == username))
    user = db_session.exec(statement).first()

    if user is None:
        raise credentials_exception
    return user
