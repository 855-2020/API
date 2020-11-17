from sqlalchemy import Float, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship, backref

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    first_name = Column(String(100), index=True, nullable=False)
    last_name = Column(String(200), index=True, nullable=False)

    roles = relationship('Role', secondary=lambda: user_roles)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    users = relationship('User', secondary=lambda: user_roles)


user_roles = Table('user_roles', Base.metadata,
                   Column('user', Integer, ForeignKey(User.id), primary_key=True),
                   Column('role', Integer, ForeignKey(Role.id), primary_key=True),
                   )


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)

    coefs = relationship("Coefficient", foreign_keys="coefs.source_id", back_populates="source")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(10))
    desc = Column(String(100))


class Coefficient(Base):
    __tablename__ = "coefs"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sectors.id"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("sectors.id"), nullable=False, index=True)
    value = Column(Float, nullable=False)

    source = relationship("Sector", foreign_keys=source_id)
    target = relationship("Sector", foreign_keys=target_id)


class CoefficientActivity(Base):
    __tablename__ = "coefs_activity"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    sector_id = Column(
        Integer, ForeignKey("sectors.id"), nullable=False, index=True
    )
    activity_id = Column(
        Integer, ForeignKey("sectors.id"), nullable=False, index=True
    )
    value = Column(Float, nullable=False)

    sector = relationship("Sectors")
    activity = relationship("Activity")
