from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models
from ..deps import get_db
from ..schemas import User, UserCreate
from ..security import get_current_user, get_admin_user, get_password_hash

router = APIRouter()


@router.get('/me', response_model=User)
def read_self(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post('/create', response_model=User)
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


@router.get('/list', response_model=List[User],
            response_model_include={'id', 'firstname', 'lastname'},
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
