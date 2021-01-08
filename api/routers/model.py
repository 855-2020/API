import numpy
from numpy import ndarray

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models
from ..deps import get_db
from ..schemas import Model, SimInput, SimOutput
from ..security import get_current_user_optional, get_admin_user, get_current_user

router = APIRouter()


@router.get('/list', response_model=List[Model],
            response_model_exclude={'economic_matrix', 'leontief_matrix', 'sectors'})
def list_sectors(db: Session = Depends(get_db), db_user: Optional[models.User] = Depends(get_current_user_optional)):
    current_roles = crud.query_user_role_list(db, db_user.id) if db_user is not None else crud.query_guest_role(db)
    return crud.get_models_filtered_role(db, current_roles)


@router.get('/{model_id}/get', response_model=Model)
def list_sectors(model_id: int, db: Session = Depends(get_db),
                 db_user: Optional[models.User] = Depends(get_current_user_optional)):
    current_roles = crud.query_user_role_list(db, db_user.id) if db_user is not None else crud.query_guest_role(db)
    model = crud.get_model(db, model_id, current_roles)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return model


@router.post('/{model_id}/simulate', response_model=SimOutput)
def list_sectors(model_id: int, values: SimInput,
                 db: Session = Depends(get_db), db_user: Optional[models.User] = Depends(get_current_user_optional)):
    if db_user is None:
        role_ids = crud.query_guest_role(db)
    else:
        # noinspection PyUnresolvedReferences
        role_ids = db.query(models.Role.id).select_entity_from(db_user.roles.subquery())
    model = crud.get_model(db, model_id, role_ids)

    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    L: ndarray = model.leontief_matrix
    x = numpy.zeros((L.shape[0], 1), dtype=numpy.float)
    for (idx, val) in values.values.items():
        if idx > x.size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        x[idx, 0] = val
    # noinspection PyTypeChecker
    categories_sorted = sorted(model.categories, key=lambda c: c.pos)
    impact = numpy.array([list(map(lambda c: c.coefficient, categories_sorted))])
    y: ndarray = L @ x
    details: ndarray = y @ impact
    return {
        "categories": categories_sorted,
        "result": numpy.squeeze(y).tolist(),
        "detailed": details.tolist()
    }


@router.post('/{model_id}/add_roles', dependencies=[Depends(get_admin_user)])
def add_model_roles(model_id: int, role_ids: List[int], db: Session = Depends(get_db)):
    db_model: models.Model = db.query(models.Model).filter_by(id=model_id).scalar()
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    new_roles: list[models.Role] = db.query(models.Role).filter(models.Role.id.in_(role_ids)).all()
    db_model.roles.extend(new_roles)
    db.commit()


@router.post('/{model_id}/remove_roles', dependencies=[Depends(get_admin_user)])
def remove_model_roles(model_id: int, role_ids: List[int], db: Session = Depends(get_db)):
    db_model: models.Model = db.query(models.Model).filter_by(id=model_id).scalar()
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    stmt = (models.model_roles.delete()
            .where(models.model_roles.c.model_id == model_id)
            .where(models.model_roles.c.role_id.in_(role_ids)))
    db.execute(stmt)
    db.commit()
