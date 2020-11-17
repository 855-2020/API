from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_db
from ..schemas import User, UserCreate
from ..security import get_current_user, get_admin_user, get_password_hash

router = APIRouter()


@router.get('/me', response_model=User)
def read_self(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post('/create', response_model=User, dependencies=[Depends(get_admin_user)])
def create_new(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(username=user.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    user.password = get_password_hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    return new_user
