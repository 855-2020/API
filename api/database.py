"""
Utilitary methods to setup an SQLAlchemy session
"""
import pickle

import numpy
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy import create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class NumpyColumnType(types.TypeDecorator):
    impl = types.LargeBinary

    def process_bind_param(self, value: numpy.ndarray, dialect: Dialect) -> bytes:
        return pickle.dumps(value)

    def process_result_value(self, value: bytes, dialect: Dialect) -> numpy.ndarray:
        return pickle.loads(value)

    def process_literal_param(self, value, dialect):
        raise NotImplementedError()
