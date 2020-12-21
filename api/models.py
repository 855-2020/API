from sqlalchemy import Boolean, Float, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base, NumpyColumnType


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    username = Column(String(64), index=True, nullable=False)
    firstname = Column(String(100), index=True, nullable=False)
    lastname = Column(String(200), index=True, nullable=False)
    password = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)

    roles = relationship('Role', lazy='dynamic', secondary=lambda: user_roles)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    users = relationship('User', lazy='dynamic', secondary=lambda: user_roles)


user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', Integer, ForeignKey(User.id), primary_key=True),
                   Column('role_id', Integer, ForeignKey(Role.id), primary_key=True),
                   )


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)

    economic_matrix = Column(NumpyColumnType, nullable=False)
    leontief_matrix = Column(NumpyColumnType, nullable=False)

    sectors = relationship("Sector", backref="model")
    roles = relationship('Role', lazy='dynamic', secondary=lambda: model_roles)


model_roles = Table('model_roles', Base.metadata,
                    Column('model_id', Integer, ForeignKey(Model.id), primary_key=True),
                    Column('role_id', Integer, ForeignKey(Role.id), primary_key=True),
                    )


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    model_id = Column(Integer, ForeignKey(Model.id))
    value_added = Column(Float, nullable=False)


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(10))
    desc = Column(String(100))


class ActivityCoefficient(Base):
    __tablename__ = "coefs_activity"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    sector_id = Column(
        Integer, ForeignKey("sectors.id"), nullable=False, index=True
    )
    activity_id = Column(
        Integer, ForeignKey("activities.id"), nullable=False, index=True
    )
    value = Column(Float, nullable=False)

    sector = relationship("Sector")
    activity = relationship("Activity")
