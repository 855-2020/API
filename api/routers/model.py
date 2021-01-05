import numpy
from numpy import ndarray

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models
from ..deps import get_db
from ..schemas import Model, ModelInput
from ..security import get_current_user_optional

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


@router.post('/{model_id}/simulate', response_model=List[List[float]])
def list_sectors(model_id: int, values: ModelInput,
                 db: Session = Depends(get_db), db_user: Optional[models.User] = Depends(get_current_user_optional)):
    model = crud.get_model(db, model_id, db_user.roles if db_user is not None else crud.query_guest_role(db))
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    L: ndarray = model.leontief_matrix
    x = numpy.zeros((L.shape[0], 1), dtype=numpy.float)
    for (idx, val) in values.values.items():
        if idx > x.size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        x[idx, 0] = val
    impct = numpy.array([[0.2, 0.5, 0.4]])  # TODO
    y: ndarray = L @ x
    details: ndarray = y @ impct
    return numpy.concatenate((y, details), axis=1).tolist() # TODO model
