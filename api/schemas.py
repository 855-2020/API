"""
Pydantic schemas
"""

from typing import List, Optional

# pylint: disable=no-name-in-module
import numpy
from pydantic import BaseModel, SecretStr, validator


class UserBase(BaseModel):
    """Class base for User"""

    username: str
    firstname: str
    lastname: str
    email: str


class UserCreate(UserBase):
    """Class for create User methods"""
    institution: str
    password: SecretStr


class User(UserBase):
    """Class User schema"""

    id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


# Sector
class SectorBase(BaseModel):
    """Class base for Sector schema"""

    name: str
    value_added: float


class SectorCreate(SectorBase):
    """Class for create Sector methods"""


class Sector(SectorBase):
    """Class Sector schema"""

    id: int
    model_id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


class ModelBase(BaseModel):
    """Class base for Model"""

    name: str
    description: Optional[str]
    sectors: List[Sector]
    economic_matrix: List[List[float]]
    leontief_matrix: List[List[float]]

    @validator('economic_matrix', 'leontief_matrix', pre=True)
    def convert_numpy(cls, value):
        return value.tolist() if isinstance(value, numpy.ndarray) else value


class ModelCreate(ModelBase):
    """Class for create Model methods"""


class Model(ModelBase):
    """Class Model schema"""

    id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


# Activity
class ActivityBase(BaseModel):
    """Class base for Activity schema"""

    name: str
    desc: str


class ActivityCreate(ActivityBase):
    """Class for create Activity methods"""


class Activity(ActivityBase):
    """Class Activity schema"""

    id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


# Economic Coefficient
class EconomicCoefficientBase(BaseModel):
    """Class base for Economic Coefficient schema"""

    value: str


class EconomicCoefficientCreate(EconomicCoefficientBase):
    """Class for create Economic Coefficient methods"""


class EconomicCoefficient(EconomicCoefficientBase):
    """Class Economic Coefficient schema"""

    id: int
    source_id: int
    target_id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


# Leontief Coefficient
class LeontiefCoefficientBase(BaseModel):
    """Class base for Leontief Coefficient schema"""

    value: str


class LeontiefCoefficientCreate(LeontiefCoefficientBase):
    """Class for create Leontief Coefficient methods"""


class LeontiefCoefficient(LeontiefCoefficientBase):
    """Class Leontief Coefficient schema"""

    id: int
    source_id: int
    target_id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


# Activity Coefficient
class ActivityCoefficientBase(BaseModel):
    """Class base for Coefficient_Activity schema"""

    value: float


class ActivityCoefficientCreate(ActivityCoefficientBase):
    """Class for create CoefficientActivityCreate methods"""


class ActivityCoefficient(ActivityCoefficientBase):
    """Class CoefficientActivity schema"""

    id: int
    sector_id: int
    activity_id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True
