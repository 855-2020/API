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
    """
    Returns user information from logged-in user
    """
    return current_user


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=User)
def create_new(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create new user
    """
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
    db.flush()
    return new_user


@router.post('/me/update_password')
def update_self_password(password: UserPassword, db: Session = Depends(get_db),
              current_user: models.User = Depends(get_current_user)):
    """
    Updates password for logged-in user
    """
    matches = verify_password(password.current_password.get_secret_value(), current_user.password)
    if not matches:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    current_user.password = get_password_hash(password.new_password.get_secret_value())
    db.commit()
    db.flush()


@router.post('/{user_id}/update_password', dependencies=[Depends(get_admin_user)])
def update_password(user_id: int, password: UserPassword, db: Session = Depends(get_db)):
    """
    Update password for any user [Admin only]
    """
    db_user = db.query(models.User).filter_by(id=user_id).scalar()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db_user.password = get_password_hash(password.new_password.get_secret_value())
    db.commit()
    db.flush()


@router.put('/me/update')
def update_self(user: User, db: Session = Depends(get_db),
              current_user: models.User = Depends(get_current_user)):
    """
    Update user information for logged-in user
    """
    for attr in ["firstname", "lastname", "email", "institution"]:
        setattr(current_user, attr, getattr(user, attr))
    db.commit()
    db.flush()


@router.get('/list', response_model=List[User],
            dependencies=[Depends(get_admin_user)])
def list_all_users(db: Session = Depends(get_db)):
    """
    Lists all users [Admin only]
    """
    return db.query(models.User).all()


@router.get('/{user_id}/details', response_model=User, dependencies=[Depends(get_admin_user)])
def user_details(user_id: int, db: Session = Depends(get_db)):
    """
    Returns details for a single user [Admin only]
    """
    user = db.query(models.User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.put('/{user_id}/update', dependencies=[Depends(get_admin_user)])
def update_user(user: User, db: Session = Depends(get_db)):
    """
    Update user information for any user [Admin only]
    """
    db_user: models.User = db.query(models.User).filter_by(id=user.id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for attr in ["firstname", "lastname", "email", "institution"]:
        setattr(db_user, attr, getattr(user, attr))
    db.commit()
    db.flush()


@router.post('/{user_id}/add_roles', dependencies=[Depends(get_admin_user)])
def add_user_roles(user_id: int, role_ids: List[int], db: Session = Depends(get_db)):
    """
    Add new roles for any user [Admin only]
    """
    db_user: models.User = db.query(models.User).filter_by(id=user_id).scalar()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    new_roles: list[models.Role] = db.query(models.Role).filter(models.Role.id.in_(role_ids)).all()
    db_user.roles.extend(new_roles)
    db.commit()
    db.flush()


@router.post('/{user_id}/remove_roles', dependencies=[Depends(get_admin_user)])
def remove_user_roles(user_id: int, role_ids: List[int], db: Session = Depends(get_db)):
    """
    Removes existing roles for any user [Admin only]
    """
    db_user: models.User = db.query(models.User).filter_by(id=user_id).scalar()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    stmt = (models.user_roles.delete()
            .where(models.user_roles.c.user_id == user_id)
            .where(models.user_roles.c.role_id.in_(role_ids)))
    db.execute(stmt)
    db.commit()
    db.flush()
