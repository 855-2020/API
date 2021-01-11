import numpy
from numpy import ndarray

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models
from ..deps import get_db
from ..schemas import Model, SimInput, SimOutput, ClonedModel
from ..security import get_current_user_optional, get_admin_user, get_current_user

router = APIRouter()


@router.get('/list', response_model=List[Model],
            response_model_exclude={'economic_matrix', 'leontief_matrix', 'catimpct_matrix', 'sectors'})
def model_list(db: Session = Depends(get_db), db_user: Optional[models.User] = Depends(get_current_user_optional)):
    if db_user is not None and crud.is_user_admin(db, db_user):
        return crud.get_models_filtered_role(db, None, True)
    current_roles = crud.query_user_role_list(db, db_user.id) if db_user is not None else crud.query_guest_role(db)
    return crud.get_models_filtered_role(db, current_roles)


@router.get('/{model_id}/get', response_model=Model)
def detail_model(model_id: int, db: Session = Depends(get_db),
                 db_user: Optional[models.User] = Depends(get_current_user_optional)):
    if model_id < 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if db_user is not None and crud.is_user_admin(db, db_user):
        return crud.get_model(db, model_id, None, True)
    current_roles = crud.query_user_role_list(db, db_user.id) if db_user is not None else crud.query_guest_role(db)
    model = crud.get_model(db, model_id, current_roles)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return model


# noinspection PyUnresolvedReferences
@router.post('/{model_id}/clone', response_model=ClonedModel)
def clone_model(model_id: int, db: Session = Depends(get_db),
                db_user: models.User = Depends(get_current_user)):
    if model_id < 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if crud.is_user_admin(db, db_user):
        model = crud.get_model(db, model_id, None, True)
    else:
        current_roles = crud.query_user_role_list(db, db_user.id)
        model = crud.get_model(db, model_id, current_roles)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    tmp = models.TempModel(name=model.name, description=model.description, model_id=model.id,
                           economic_matrix=model.economic_matrix, leontief_matrix=model.leontief_matrix,
                           catimpct_matrix=model.catimpct_matrix, owner=db_user)
    db.add(tmp)
    tmp.sectors.extend(
        map(lambda s: models.TempSector(name=s.name, pos=s.pos, value_added=s.value_added),
            model.sectors))
    tmp.categories.extend(map(
        lambda c: models.TempCategory(name=c.name, pos=c.pos, description=c.description, unit=c.unit),
        model.categories))
    db.commit()
    db.flush()
    return {
        "id": -tmp.id,
        "name": tmp.name,
        "description": tmp.description,
        "sectors": tmp.sectors,
        "categories": tmp.categories,
        "economic_matrix": tmp.economic_matrix,
        "catimpct_matrix": tmp.catimpct_matrix,
    }


# noinspection PyUnresolvedReferences
@router.post('/{model_id}/persist')
def persist_model(model_id: int, db: Session = Depends(get_db),
                  db_user: models.User = Depends(get_current_user)):
    if model_id >= 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    tmp_model = crud.get_temporary_model(db, -model_id, db_user, crud.is_user_admin(db, db_user))
    if tmp_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    new_model = models.Model(name=tmp_model.name, description=tmp_model.description,
                             economic_matrix=tmp_model.economic_matrix, leontief_matrix=tmp_model.leontief_matrix,
                             catimpct_matrix=tmp_model.catimpct_matrix)
    db.add(new_model)
    new_model.sectors.extend(
        map(lambda s: models.Sector(name=s.name, pos=s.pos, value_added=s.value_added),
            tmp_model.sectors))
    new_model.categories.extend(map(
        lambda c: models.Category(name=c.name, pos=c.pos, description=c.description, unit=c.unit),
        tmp_model.categories))
    new_model.roles.extend(tmp_model.base_model.roles.all())
    db.delete(tmp_model)
    db.commit()
    db.flush()


@router.post('/{model_id}/simulate', response_model=SimOutput)
def model_sim(model_id: int, values: SimInput,
              db: Session = Depends(get_db), db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # noinspection PyPep8Naming
    L: ndarray = model.leontief_matrix
    x = numpy.zeros((L.shape[0], 1), dtype=numpy.float)
    for (idx, val) in values.values.items():
        if idx > x.size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        x[idx, 0] = val
    # noinspection PyTypeChecker
    categories_sorted = sorted(model.categories, key=lambda c: c.pos)
    y: ndarray = L @ x
    details: ndarray = y * model.catimpct_matrix.T
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


@router.delete('/{model_id}', dependencies=[Depends(get_admin_user)])
def remove_model_roles(model_id: int, db: Session = Depends(get_db)):
    if model_id >= 0:
        db_model: models.Model = db.query(models.Model).filter_by(id=model_id).scalar()
    else:
        db_model: models.TempModel = db.query(models.TempModel).filter_by(id=-model_id).scalar()
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(db_model)
    db.commit()
    db.flush()
