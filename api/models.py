from sqlalchemy import Float, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship, backref

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    username = Column(String(64), index=True, nullable=False)
    firstname = Column(String(100), index=True, nullable=False)
    lastname = Column(String(200), index=True, nullable=False)
    password = Column(String, nullable=False)

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


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)

    coefs = relationship("LeontiefCoefficient", lazy="dynamic", foreign_keys=lambda: LeontiefCoefficient.source_id,
                         back_populates="source")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(10))
    desc = Column(String(100))


class LeontiefCoefficient(Base):
    __tablename__ = "coefs_leontief"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sectors.id"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("sectors.id"), nullable=False, index=True)
    value = Column(Float, nullable=False)

    source = relationship("Sector", foreign_keys=[source_id])
    target = relationship("Sector", foreign_keys=[target_id])


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

    # sector = relationship("Sectors")
    activity = relationship("Activity")
