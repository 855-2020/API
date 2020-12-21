"""
CRUD
"""

# pylint: disable=C0321
# pylint: disable=no-name-in-module

from typing import List
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


# Model
def get_model(db: Session, model_id: int):
    """Retrieve an model by id"""

    return db.query(models.Model).filter_by(id=model_id).first()


def get_models_filtered_role(db: Session, roles: Query):
    """Retrieve models filtered by roles"""

    return (db.query(models.Model)
            .join(models.Model.roles)
            .filter(models.Role.id.in_(roles.subquery()))
            .all())


# Activity
def get_activity(db: Session, activity_id: int):
    """Retrieve an activity by id"""

    return db.query(models.Activity).filter_by(id=activity_id).first()


def save_activity(db: Session, activity: schemas.Activity):
    """Save new activity"""

    db_activity = models.Activity(**activity.dict())
    db.merge(db_activity)
    db.commit()
    return db_activity


# Economic Coefficient
def get_economic_coefficients_by_source(db: Session, keys: List[int]):
    """List of all Economic coefficient by source id"""

    return (db.query(models.EconomicCoefficient)
            .filter(models.EconomicCoefficient.source_id.in_(keys))
            .all())


def get_economic_coefficient(db: Session, coefficient_id: int):
    """Retrieve an Economic coefficient by id"""

    return db.query(models.EconomicCoefficient).filter_by(id=coefficient_id).first()


def save_econonomic_coefficient(db: Session, coefficient: schemas.EconomicCoefficient):
    """Save new Economic coefficient"""

    db_coefficient = models.EconomicCoefficient(**coefficient.dict())
    db.merge(db_coefficient)
    db.commit()
    return db_coefficient


# Leontief Coefficient
def get_leontief_coefficients_by_source(db: Session, keys: List[int]):
    """List of all Leontief Coefficients by source id"""

    return (db.query(models.LeontiefCoefficient)
            .filter(models.LeontiefCoefficient.source_id.in_(keys))
            .all())


def get_leontief_coefficient(db: Session, coefficient_id: int):
    """Retrieve an Leontief Coefficient by id"""

    return db.query(models.LeontiefCoefficient).filter_by(id=coefficient_id).first()


def save_leontief_coefficient(db: Session, coefficient: schemas.LeontiefCoefficient):
    """Save new Leontief Coefficient"""

    db_coefficient = models.LeontiefCoefficient(**coefficient.dict())
    db.merge(db_coefficient)
    db.commit()
    return db_coefficient


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


# Activity Coefficient
def get_coefficient_activities_by_sector(db: Session, sector_id: int):
    """List of all CoefficientActivities by sector id"""

    return (db.query(models.ActivityCoefficient)
            .filter(models.ActivityCoefficient.sector_id == sector_id)
            .all())


def get_coefficient_activity(db: Session, coefficient_id: int):
    """Retrieve an CoefficientActivity by id"""

    return db.query(models.ActivityCoefficient).filter_by(id=coefficient_id).first()


def save_coefficientactivity(db: Session, coefficient_activities: schemas.ActivityCoefficient):
    """Save new CoefficientActivity"""

    db_cefficient_activities = models.ActivityCoefficient(**coefficient_activities.dict())
    db.merge(db_cefficient_activities)
    db.commit()
    return db_cefficient_activities
