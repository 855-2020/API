from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_db
from ..schemas import Sector

router = APIRouter()


@router.get('/{model_id}/list', response_model=List[Sector])
def list_sectors(_model_id: int, db: Session = Depends(get_db)):
    # TODO check user roles against model
    resp = db.query(models.Sector).all()
    return list(map(lambda s: {'id': s.id, 'name': s.name}, resp))
