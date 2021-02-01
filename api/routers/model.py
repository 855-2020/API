import numpy
from numpy import ndarray

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models
from ..deps import get_db
from ..schemas import Model, SimInput, SimOutput, ClonedModel, SectorCreate, CategoryCreate, CoefsInput, \
    IdentifierModel, Sector, Category
from ..security import get_current_user_optional, get_admin_user, get_current_user

router = APIRouter()


@router.get('/list', response_model=List[Model],
            response_model_exclude={'economic_matrix', 'leontief_matrix', 'catimpct_matrix', 'sectors'})
def model_list(db: Session = Depends(get_db), db_user: Optional[models.User] = Depends(get_current_user_optional)):
    """
    Lists all models that logged-in user has access
    [Admin: lists all models]
    """
    if db_user is not None and crud.is_user_admin(db, db_user):
        return crud.get_models_filtered_role(db, None, True)
    current_roles = crud.query_user_role_list(db, db_user.id) if db_user is not None else crud.query_guest_role(db)
    return crud.get_models_filtered_role(db, current_roles)


@router.get('/{model_id}/get', response_model=Model)
def detail_model(model_id: int, db: Session = Depends(get_db),
                 db_user: Optional[models.User] = Depends(get_current_user_optional)):
    """
    Returns data for model, including the full matrices
    """
    if model_id < 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if db_user is not None and crud.is_user_admin(db, db_user):
        return crud.get_model(db, model_id, None, True)
    current_roles = crud.query_user_role_list(db, db_user.id) if db_user is not None else crud.query_guest_role(db)
    model = crud.get_model(db, model_id, current_roles)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return model


@router.post('/new', response_model=Model, dependencies=[Depends(get_admin_user)])
def new_model(name: str, role_ids: List[int], description: Optional[str] = None, db: Session = Depends(get_db)):
    new_model = models.Model(name=name, description=description)
    new_model.economic_matrix = numpy.array([], dtype=float, ndmin=2)
    new_model.leontief_matrix = numpy.array([], dtype=float, ndmin=2)
    new_model.catimpct_matrix = numpy.array([], dtype=float, ndmin=2)
    roles = db.query(models.Role).filter(models.Role.id.in_(role_ids)).all()
    new_model.roles.extend(roles)
    db.add(new_model)
    db.commit()
    db.flush()
    return new_model


@router.post('/{model_id}/modify')
def modify_model(model_id: int, name: Optional[str], description: Optional[str], db: Session = Depends(get_db),
                 db_user: models.User = Depends(get_admin_user)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if name is not None:
        model.name = name
    if description is not None:
        model.description = description
    db.commit()
    db.flush()


# noinspection PyUnresolvedReferences,PyTypeChecker
@router.post('/{model_id}/clone', response_model=ClonedModel)
def clone_model(model_id: int, db: Session = Depends(get_db),
                db_user: models.User = Depends(get_current_user)):
    """
    Create a new temporary model from a base model.
    Logged-in user becomes the owner of this model and can make changes.
    """
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


# noinspection PyUnresolvedReferences,PyTypeChecker
@router.post('/{model_id}/persist', response_model=IdentifierModel)
def persist_model(model_id: int, db: Session = Depends(get_db),
                  db_user: models.User = Depends(get_current_user)):
    """
    Converts temporary model to a regular model
    """
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
    return {
      "id": new_model.id,
    }


@router.post('/{model_id}/simulate', response_model=SimOutput)
def model_sim(model_id: int, values: SimInput,
              db: Session = Depends(get_db), db_user: Optional[models.User] = Depends(get_current_user_optional)):
    """
    Run a simulation using the model and the input vector

    """
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if values.change is not None:
        change = numpy.array(values.change, dtype=numpy.float)
        if change.shape != model.leontief_matrix.shape:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        # noinspection PyPep8Naming
        A: ndarray = (1+change)*model.economic_matrix
        L: ndarray = numpy.linalg.inv(numpy.eye(A.shape[0])-A)
    else:
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


@router.post('/{model_id}/sector/new')
def model_new_sector(model_id: int, sector: SectorCreate,
                     db: Session = Depends(get_db),
                     db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if sector.pos >= model.economic_matrix.shape[1]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    cls = models.TempSector if model_id < 0 else models.Sector
    # noinspection PyArgumentList
    new_sector = cls(name=sector.name, model_id=model.id, pos=sector.pos, value_added=sector.value_added)
    db.query(cls).filter_by(model_id=model.id).filter(cls.pos >= new_sector.pos).update({'pos': cls.pos + 1})
    db.add(new_sector)
    model.economic_matrix = numpy.insert(model.economic_matrix, new_sector.pos, numpy.array(sector.reverse), 1)
    model.economic_matrix = numpy.insert(model.economic_matrix, new_sector.pos, numpy.array(sector.direct), 0)
    model.leontief_matrix = numpy.linalg.inv(numpy.eye(model.economic_matrix.shape[0]) - model.economic_matrix)
    model.catimpct_matrix = numpy.insert(model.catimpct_matrix, new_sector.pos, numpy.array(sector.impacts), 1)
    db.commit()
    db.flush()


@router.post('/{model_id}/sector/{sector_pos}/modify', response_model=Sector)
def model_modify_sector(model_id: int, sector_pos: int, name: Optional[str] = None, value_added: Optional[float] = None,
                        db: Session = Depends(get_db),
                        db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    cls = models.TempSector if model_id < 0 else models.Sector
    sector = db.query(cls).filter_by(model_id=model.id, pos=sector_pos).scalar()
    if sector is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if name is not None:
        sector.name = name
    if value_added is not None:
        sector.value_added = value_added

    db.commit()
    db.flush()
    return sector


@router.delete('/{model_id}/sector/{sector_pos}')
def model_delete_sector(model_id: int, sector_pos: int,
                        db: Session = Depends(get_db),
                        db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    cls = models.TempSector if model_id < 0 else models.Sector
    sector = db.query(cls).filter_by(model_id=model.id, pos=sector_pos).scalar()
    if sector is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.query(cls).filter_by(model_id=model.id) \
        .filter(cls.pos >= sector_pos).update({'pos': cls.pos - 1})
    db.delete(sector)
    model.economic_matrix = numpy.delete(model.economic_matrix, sector_pos, 0)
    model.economic_matrix = numpy.delete(model.economic_matrix, sector_pos, 1)
    model.leontief_matrix = numpy.linalg.inv(numpy.eye(model.economic_matrix.shape[0]) - model.economic_matrix)
    model.catimpct_matrix = numpy.delete(model.catimpct_matrix, sector_pos, 1)
    db.commit()
    db.flush()


@router.post('/{model_id}/coefs/update')
def model_coefs_update(model_id: int, coefs: CoefsInput, db: Session = Depends(get_db),
                       db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    model.economic_matrix = numpy.array(coefs.values, dtype=numpy.float)
    model.leontief_matrix = numpy.linalg.inv(numpy.eye(model.economic_matrix.shape[0]) - model.economic_matrix)
    db.commit()
    db.flush()


@router.post('/{model_id}/impacts/update')
def model_impacts_update(model_id: int, coefs: CoefsInput, db: Session = Depends(get_db),
                         db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    model.catimpct_matrix = numpy.array(coefs.values, dtype=numpy.float)
    db.commit()
    db.flush()


@router.post('/{model_id}/impact/new')
def model_new_impact(model_id: int, category: CategoryCreate,
                     db: Session = Depends(get_db),
                     db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    cls = models.TempCategory if model_id < 0 else models.Category
    # noinspection PyArgumentList
    new_category = cls(name=category.name, model_id=model.id, pos=category.pos, description=category.description,
                       unit=category.unit)
    db.query(cls).filter_by(model_id=model.id).filter(
        cls.pos >= new_category.pos).update({'pos': cls.pos + 1})
    db.add(new_category)
    model.catimpct_matrix = numpy.insert(model.catimpct_matrix, new_category.pos, numpy.array(category.impacts), 0)
    db.commit()
    db.flush()


@router.post('/{model_id}/impact/{impact_pos}/modify', response_model=Category)
def model_modify_sector(model_id: int, impact_pos: int, name: Optional[str] = None, description: Optional[str] = None,
                        unit: Optional[str] = None, db: Session = Depends(get_db),
                        db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    cls = models.TempCategory if model_id < 0 else models.Category
    category = db.query(cls).filter_by(model_id=model.id, pos=impact_pos).scalar()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if name is not None:
        category.name = name
    if description is not None:
        category.description = description
    if unit is not None:
        category.unit = unit

    db.commit()
    db.flush()
    return category

@router.delete('/{model_id}/impact/{impact_pos}')
def model_delete_impact(model_id: int, impact_pos: int,
                        db: Session = Depends(get_db),
                        db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.fetch_model(db, model_id, db_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    cls = models.TempCategory if model_id < 0 else models.Category
    category = db.query(cls).filter_by(model_id=model.id, pos=impact_pos).scalar()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.query(cls).filter_by(model_id=model.id).filter(cls.pos >= impact_pos).update({'pos': cls.pos - 1})
    db.delete(category)
    model.catimpct_matrix = numpy.delete(model.catimpct_matrix, impact_pos, 0)
    db.commit()
    db.flush()


@router.post('/{model_id}/add_roles', dependencies=[Depends(get_admin_user)])
def add_model_roles(model_id: int, role_ids: List[int], db: Session = Depends(get_db)):
    if model_id < 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db_model: models.Model = db.query(models.Model).filter_by(id=model_id).scalar()
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    new_roles: list[models.Role] = db.query(models.Role).filter(models.Role.id.in_(role_ids)).all()
    db_model.roles.extend(new_roles)
    db.commit()


@router.post('/{model_id}/remove_roles', dependencies=[Depends(get_admin_user)])
def remove_model_roles(model_id: int, role_ids: List[int], db: Session = Depends(get_db)):
    if model_id < 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db_model: models.Model = db.query(models.Model).filter_by(id=model_id).scalar()
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    stmt = (models.model_roles.delete()
            .where(models.model_roles.c.model_id == model_id)
            .where(models.model_roles.c.role_id.in_(role_ids)))
    db.execute(stmt)
    db.commit()


@router.delete('/{model_id}', dependencies=[Depends(get_admin_user)])
def remove_model_roles(model_id: int, db: Session = Depends(get_db), db_user: models.User = Depends(get_current_user)):
    if model_id >= 0:
        if not crud.is_user_admin(db, db_user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        db_model: models.Model = db.query(models.Model).filter_by(id=model_id).scalar()
    else:
        db_model: models.TempModel = db.query(models.TempModel).filter_by(id=-model_id, user_id=db_user.id).scalar()
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(db_model)
    db.commit()
    db.flush()
