"""
CRUD
"""

# pylint: disable=C0321
# pylint: disable=no-name-in-module

from sqlalchemy.orm import Session

from . import models, schemas


# Model
def get_models(db: Session):
    """List of all models"""

    return db.query(models.Model)


def get_model(db: Session, model_id: int):
    """Retrieve an model by id"""

    return db.query(models.Model).filter(models.Model.id == model_id).first()


def save_model(db: Session, model: schemas.Model):
    """Save new model"""

    db_model = models.Model(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Activity
def get_activities(db: Session):
    """List of all activities"""

    return db.query(models.Activity)


def get_activity(db: Session, activity_id: int):
    """Retrieve an activity by id"""

    return db.query(models.Activity).filter(models.Activity.id == activity_id).first()


def save_activity(db: Session, activity: schemas.Activity):
    """Save new activity"""

    db_activity = models.Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


# Economic Coefficient
def get_economic_coefficients(db: Session):
    """List of all Economic coefficient"""

    return db.query(models.EconomicCoefficient)


def get_economic_coefficient(db: Session, coefficient_id: int):
    """Retrieve an Economic coefficient by id"""

    return (
        db.query(models.EconomicCoefficient)
        .filter(models.EconomicCoefficient.id == coefficient_id)
        .first()
    )


def save_econonomic_coefficient(db: Session, coefficient: schemas.EconomicCoefficient):
    """Save new Economic coefficient"""

    db_coefficient = models.EconomicCoefficient(**coefficient.dict())
    db.add(db_coefficient)
    db.commit()
    db.refresh(db_coefficient)
    return db_coefficient


# Leontief Coefficient
def get_leontief_coefficients(db: Session):
    """List of all Leontief Coefficients"""

    return db.query(models.LeontiefCoefficient)


def get_leontief_coefficient(db: Session, coefficient_id: int):
    """Retrieve an Leontief Coefficient by id"""

    return (
        db.query(models.LeontiefCoefficient)
        .filter(models.LeontiefCoefficient.id == coefficient_id)
        .first()
    )


def save_leontief_coefficient(db: Session, coefficient: schemas.LeontiefCoefficient):
    """Save new Leontief Coefficient"""

    db_coefficient = models.LeontiefCoefficient(**coefficient.dict())
    db.add(db_coefficient)
    db.commit()
    db.refresh(db_coefficient)
    return db_coefficient


# Sector
def get_sectors(db: Session):
    """List of all sectors"""

    return db.query(models.Sector)


def get_sector(db: Session, sector_id: int):
    """Retrieve an sector by id"""

    return db.query(models.Sector).filter(models.Sector.id == sector_id).first()


def save_sector(db: Session, sector: schemas.Sector):
    """Save new sector"""

    db_sector = models.Sector(**sector.dict())
    db.add(db_sector)
    db.commit()
    db.refresh(db_sector)
    return db_sector


# Activity Coefficient
def get_coefficient_activities(db: Session):
    """List of all CoefficientActivities"""

    return db.query(models.ActivityCoefficient)


def get_coefficient_activity(db: Session, coefficient_id: int):
    """Retrieve an CoefficientActivity by id"""

    return (
        db.query(models.ActivityCoefficient)
        .filter(models.ActivityCoefficient.id == coefficient_id)
        .first()
    )


def save_coefficientactivity(
    db: Session, coefficient_activities: schemas.ActivityCoefficient
):
    """Save new CoefficientActivity"""

    db_cefficient_activities = models.ActivityCoefficient(
        **coefficient_activities.dict()
    )
    db.add(db_cefficient_activities)
    db.commit()
    db.refresh(db_cefficient_activities)
    return db_cefficient_activities
