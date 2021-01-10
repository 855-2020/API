"""
Pydantic schemas
"""

from typing import List, Optional, Dict

# pylint: disable=no-name-in-module
import numpy
from pydantic import BaseModel, EmailStr, SecretStr, validator
from sqlalchemy.orm import Query


class RoleBase(BaseModel):
    name: str
    description: Optional[str]


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    """Class base for User"""

    username: str
    firstname: str
    lastname: str
    email: EmailStr


class UserCreate(UserBase):
    """Class for create User methods"""
    institution: Optional[str]
    password: SecretStr
    agreed_terms: bool


class User(UserBase):
    """Class User schema"""

    id: int
    institution: Optional[str]
    roles: List[Role]

    @validator('roles', pre=True)
    def fetch_dynamic(cls, value):
        return value.all() if isinstance(value, Query) else value

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


class UserPassword(BaseModel):
    current_password: SecretStr
    new_password: SecretStr


# Sector
class SectorBase(BaseModel):
    """Class base for Sector schema"""

    name: str
    value_added: float


class SectorCreate(SectorBase):
    """Class for create Sector methods"""
    model_id: int


class Sector(SectorBase):
    """Class Sector schema"""

    id: int

    class Config:
        """Class used to provide configurations to Pydantic"""

        orm_mode = True


class CategoryBase(BaseModel):
    name: str
    pos: int
    description: str
    unit: str


class CategoryCreate(CategoryBase):
    model_id: int


class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class ModelBase(BaseModel):
    """Class base for Model"""

    name: str
    description: Optional[str]
    sectors: List[Sector]
    categories: List[Category]
    economic_matrix: List[List[float]]
    leontief_matrix: List[List[float]]

    roles: List[Role]

    @validator('roles', pre=True)
    def fetch_dynamic(cls, value):
        return value.all() if isinstance(value, Query) else value

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


class SimInput(BaseModel):
    values: Dict[int, float]


class SimOutput(BaseModel):
    categories: List[Category]
    result: List[float]
    detailed: List[List[float]]
