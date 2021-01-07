from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models
from ..deps import get_db
from ..schemas import User, UserCreate, UserPassword
from ..security import get_current_user, get_admin_user, get_password_hash, verify_password

router = APIRouter()


@router.get('/me', response_model=User)
def read_self(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=User)
def create_new(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(username=user.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    if db.query(models.User).filter_by(email=user.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    user.password = get_password_hash(user.password.get_secret_value())
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    return new_user


@router.post('/me/update_password')
def read_self(password: UserPassword, db: Session = Depends(get_db),
              current_user: models.User = Depends(get_current_user)):
    matches = verify_password(password.current_password.get_secret_value(), current_user.password)
    if not matches:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    current_user.password = get_password_hash(password.new_password.get_secret_value())
    db.commit()


@router.post('/{user_id}/update_password', dependencies=[Depends(get_admin_user)])
def read_self(user_id: int, password: UserPassword, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter_by(id = user_id).scalar()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db_user.password = get_password_hash(password.new_password.get_secret_value())
    db.commit()


@router.get('/list', response_model=List[User],
            dependencies=[Depends(get_admin_user)])
def list_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.get('/{user_id}/details', response_model=User, dependencies=[Depends(get_admin_user)])
def list_all_users(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.put('/{user_id}/update', dependencies=[Depends(get_admin_user)])
def list_all_users(user: User, db: Session = Depends(get_db)):
    db_user: models.User = db.query(models.User).filter_by(id=user.id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for attr in ["firstname", "lastname", "email"]:
        setattr(db_user, attr, getattr(user, attr))
    db.commit()
