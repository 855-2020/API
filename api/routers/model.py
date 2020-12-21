from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, models
from ..deps import get_db
from ..schemas import Model
from ..security import get_current_user_optional

router = APIRouter()


@router.get('/list', response_model=List[Model])
def list_sectors(db: Session = Depends(get_db), db_user: Optional[models.User] = Depends(get_current_user_optional)):
    current_roles = crud.query_user_role_list(db, db_user.id) if db_user is not None else crud.query_guest_role(db)
    return crud.get_models_filtered_role(db, current_roles)
