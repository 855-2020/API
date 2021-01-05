from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models
from ..deps import get_db
from ..schemas import Model, Role, RoleCreate, User
from ..security import get_admin_user

router = APIRouter()


@router.get('/list', response_model=List[Role],
            dependencies=[Depends(get_admin_user)])
def list_all_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()


@router.get('/{role_id}/users', response_model=List[User],
            dependencies=[Depends(get_admin_user)])
def list_users(role_id: int, db: Session = Depends(get_db)):
    return db.query(models.User).join(models.user_roles).filter_by(role_id=role_id).all()


@router.get('/{role_id}/models', response_model=List[Model],
            response_model_exclude={'economic_matrix', 'leontief_matrix', 'sectors'},
            dependencies=[Depends(get_admin_user)])
def list_users(role_id: int, db: Session = Depends(get_db)):
    return db.query(models.Model).join(models.model_roles).filter_by(role_id=role_id).all()


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=Role,
             dependencies=[Depends(get_admin_user)])
def list_all_users(role: RoleCreate, db: Session = Depends(get_db)):
    if db.query(models.Role).filter_by(name=role.name).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    return crud.create_role(db, role)


@router.delete('/{role_id}', response_model=int, dependencies=[Depends(get_admin_user)])
def list_all_users(role_id: int, force: bool = False, db: Session = Depends(get_db)):
    if not crud.try_delete_role(db, role_id, force):
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Role is in use")