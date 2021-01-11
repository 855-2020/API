from sqlalchemy import Boolean, Float, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base, NumpyColumnType


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    username = Column(String(64), index=True, nullable=False)
    firstname = Column(String(100), index=True, nullable=False)
    lastname = Column(String(200), index=True, nullable=False)
    email = Column(String(200), index=True, nullable=False)
    password = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    agreed_terms = Column(Boolean, nullable=False, default=False)
    institution = Column(String(200), nullable=True)

    roles = relationship('Role', lazy='dynamic', secondary=lambda: user_roles)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    users = relationship('User', lazy='dynamic', secondary=lambda: user_roles, passive_deletes=True)


user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', Integer, ForeignKey(User.id, ondelete="CASCADE"), primary_key=True),
                   Column('role_id', Integer, ForeignKey(Role.id), primary_key=True),
                   )


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)

    economic_matrix = Column(NumpyColumnType, nullable=False)
    leontief_matrix = Column(NumpyColumnType, nullable=False)
    catimpct_matrix = Column(NumpyColumnType, nullable=False)

    sectors = relationship("Sector", backref="model", cascade="all, delete-orphan", passive_deletes=True)
    categories = relationship("Category", backref="model", cascade="all, delete-orphan", passive_deletes=True)
    roles = relationship('Role', lazy='dynamic', secondary=lambda: model_roles, passive_deletes=True)


model_roles = Table('model_roles', Base.metadata,
                    Column('model_id', Integer, ForeignKey(Model.id, ondelete="CASCADE"), primary_key=True),
                    Column('role_id', Integer, ForeignKey(Role.id), primary_key=True),
                    )


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    model_id = Column(Integer, ForeignKey(Model.id, ondelete="CASCADE"), nullable=False)
    pos = Column(Integer, nullable=False)
    value_added = Column(Float, nullable=False)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    model_id = Column(Integer, ForeignKey(Model.id, ondelete="CASCADE"), nullable=False)
    pos = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    unit = Column(String, nullable=False)


class TempModel(Base):
    __tablename__ = "temp_models"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    model_id = Column(Integer, ForeignKey(Model.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    economic_matrix = Column(NumpyColumnType, nullable=False)
    leontief_matrix = Column(NumpyColumnType, nullable=False)
    catimpct_matrix = Column(NumpyColumnType, nullable=False)

    sectors = relationship("TempSector", backref="model", cascade="all, delete-orphan", passive_deletes=True)
    categories = relationship("TempCategory", backref="model", cascade="all, delete-orphan", passive_deletes=True)
    base_model = relationship("Model")
    owner = relationship("User")


class TempSector(Base):
    __tablename__ = "temp_sectors"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    model_id = Column(Integer, ForeignKey(TempModel.id, ondelete="CASCADE"), nullable=False)
    pos = Column(Integer, nullable=False)
    value_added = Column(Float, nullable=False)


class TempCategory(Base):
    __tablename__ = "temp_categories"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    model_id = Column(Integer, ForeignKey(TempModel.id, ondelete="CASCADE"), nullable=False)
    pos = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    unit = Column(String, nullable=False)
