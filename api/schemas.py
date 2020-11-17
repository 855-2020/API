"""
Pydantic schemas
"""
from typing import Optional

# pylint: disable=no-name-in-module
from pydantic import BaseModel


class UserBase(BaseModel):
    """Class base for User"""

    username: str
    firstname: str
    lastname: str


class UserCreate(UserBase):
    """Class for create User methods"""

    password: str


class User(UserBase):
    """Class User schema"""

    id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


# Activity
class ActivityBase(BaseModel):
    """Class base for Activity schema"""

    name: Optional[str] = None
    desc: Optional[str] = None


class ActivityCreate(ActivityBase):
    """Class for create Activity methods"""


class Activity(ActivityBase):
    """Class Activity schema"""

    id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


# Coefficient
class CoefficientBase(BaseModel):
    """Class base for Coefficient schema"""

    value: str


class CoefficientCreate(CoefficientBase):
    """Class for create Coefficient methods"""


class Coefficient(CoefficientBase):
    """Class Coefficient schema"""

    id: int
    source_id: int
    target_id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


# Category
class CategoryBase(BaseModel):
    """Class base for Category schema"""

    name: str


class CategoryCreate(CategoryBase):
    """Class for create Category methods"""


class Category(CategoryBase):
    """Class Category schema"""

    id: int
    parent_id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


# Coefficient_Activity
class CoefficientActivityBase(BaseModel):
    """Class base for Coefficient_Activity schema"""

    value = float


class CoefficientActivityCreate(BaseModel):
    """Class for create CoefficientActivityCreate methods"""


class CoefficientActivity(BaseModel):
    """Class CoefficientActivity schema"""

    id = int
    category_id = int
    activity_id = int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True
