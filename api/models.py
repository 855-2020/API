from sqlalchemy import Float, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # coefs = relationship("Coefficient", foreign_keys="coefs.source_id", back_populates="source")
    children = relationship("Category", backref=backref("parent", remote_side=[id]))


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10))
    desc = Column(String(100))


class Coefficient(Base):
    __tablename__ = "coefs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    value = Column(Float, nullable=False)

    source = relationship("Category", foreign_keys=source_id)
    target = relationship("Category", foreign_keys=target_id)


class CoefficientActivity(Base):
    __tablename__ = "coefs_activity"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=False, index=True
    )
    activity_id = Column(
        Integer, ForeignKey("activities.id"), nullable=False, index=True
    )
    value = Column(Float, nullable=False)

    category = relationship("Category")
    activity = relationship("Activity")
