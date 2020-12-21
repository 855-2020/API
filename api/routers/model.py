from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models
from ..deps import get_db
from ..schemas import Model
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
