import sys
from datetime import datetime, timedelta
from os import environ
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
# pylint: disable=no-name-in-module
from pydantic import BaseModel
from sqlalchemy import literal
from sqlalchemy.orm import Session

from . import crud
from .deps import get_db
from .models import User, Role, Model

SECRET_KEY = environ.get('HIDS_JWT_SECRET_KEY') or sys.exit("Must provide HIDS_JWT_SECRET_KEY env var")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


class JwtToken(BaseModel):
    access_token: str
    token_type: str


class JwtData(BaseModel):
    username: Optional[str] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    db_user = db.query(User).filter_by(username=username).first()
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> \
        Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = JwtData(username=username)
    except JWTError:
        # pylint: disable=raise-missing-from
        raise credentials_exception
    db_user = db.query(User).filter_by(username=token_data.username, enabled=True).first()
    if db_user is None:
        raise credentials_exception
    return db_user


async def get_current_user(db_user: Optional[User] = Depends(get_current_user_optional)) -> User:
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_user


async def get_admin_user(db_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    if crud.is_user_admin(db, db_user):
        return db_user
    else:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User does not have enough permission",
        headers={"WWW-Authenticate": "Bearer"},
    )


def can_access_model(user_id: int, model_id: int, db: Session) -> bool:
    quser = (db.query(Role.id)
             .select_from(User)
             .join(User.roles)
             .filter(User.id == user_id))
    qmodel = (db.query(Role.id)
              .select_from(Model)
              .join(Model.roles)
              .filter(Model.id == model_id))
    return db.query(literal(True)).filter(quser.intersect(qmodel).exists()).scalar() or False
