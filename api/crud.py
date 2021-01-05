"""
CRUD
"""

# pylint: disable=C0321
# pylint: disable=no-name-in-module

from typing import List, Optional

from sqlalchemy import literal
from sqlalchemy.orm import Session, Query

from . import models, schemas


def query_guest_role(db: Session) -> Query:
    return db.query(models.Role.id).filter_by(name="guest")


def query_user_role_list(db: Session, user_id: int) -> Query:
    return (db.query(models.Role.id)
            .select_from(models.User)
            .join(models.User.roles)
            .filter(models.User.id == user_id)
            .union(query_guest_role(db)))


def is_user_admin(db: Session, db_user: models.User) -> bool:
    return db.query(literal(True)).filter(db_user.roles.filter(models.Role.name == 'admin').exists()).scalar() or False


# Model
def get_model(db: Session, model_id: int, roles: Query) -> Optional[models.Model]:
    """Retrieve an model by id"""

    return (db.query(models.Model).filter_by(id=model_id).join(models.Model.roles)
            .filter(models.Role.id.in_(roles.subquery())).scalar())


def get_models_filtered_role(db: Session, roles: Query) -> List[models.Model]:
    """Retrieve models filtered by roles"""

    return (db.query(models.Model)
            .join(models.Model.roles)
            .filter(models.Role.id.in_(roles.subquery()))
            .all())


# Sector
def get_sector(db: Session, sector_id: int):
    """Retrieve an sector by id"""

    return db.query(models.Sector).filter_by(id=sector_id).first()


def save_sector(db: Session, sector: schemas.Sector):
    """Save new sector"""

    db_sector = models.Sector(**sector.dict())
    db.merge(db_sector)
    db.commit()
    return db_sector
