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
def get_model(db: Session, model_id: int, roles: Optional[Query], admin: bool = False) -> Optional[models.Model]:
    """Retrieve an model by id"""

    query: Query = db.query(models.Model).filter_by(id=model_id).join(models.Model.roles)
    if not admin:
        query = query.filter(models.Role.id.in_(roles.subquery()))
    return query.scalar()


def get_models_filtered_role(db: Session, roles: Optional[Query], admin: bool = False) -> List[models.Model]:
    """Retrieve models filtered by roles"""

    query: Query = db.query(models.Model).join(models.Model.roles)
    if not admin:
        query = query.filter(models.Role.id.in_(roles.subquery()))
    return query.all()


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


def create_role(db: Session, role: schemas.RoleCreate):
    db_role = models.Role(**role.dict())
    db.add(db_role)
    db.commit()
    return db_role


def try_delete_role(db: Session, role_id: int, force: bool = False) -> bool:
    model_roles_query: Query = db.query(models.model_roles).filter_by(role_id=role_id)
    user_roles_query: Query = db.query(models.user_roles).filter_by(role_id=role_id)
    in_use: Query = db.query(literal(True)).filter(model_roles_query.union(user_roles_query).exists())
    if in_use.scalar() and not force:
        return False
    db_role = db.query(models.Role).filter_by(id=role_id).scalar()
    db.delete(db_role)
    db.commit()
    return True