"""Authentification core functions"""

from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session, select
from app.config import settings
from app.db import get_session
from app.schemas import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_password_hash(password):
    """Get password hash"""
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """Check password correctness"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict,
                        expires_delta: timedelta | None = None):
    """Create user token"""
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
    """Get logined user"""
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
    except InvalidTokenError as e:
        raise credentials_exception from e

    statement = (select(schemas.User)
                 .where(schemas.User.email == username))
    user = db_session.exec(statement).first()

    if user is None:
        raise credentials_exception
    return user
