"""
Utilitary methods to setup an SQLAlchemy session
"""
import pickle
import numpy

from sqlalchemy.engine import Engine
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy import create_engine, types, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlite3 import Cursor, Connection

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(conn: Connection, _connection_record):
    cursor: Cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class NumpyColumnType(types.TypeDecorator):
    impl = types.LargeBinary

    def process_bind_param(self, value: numpy.ndarray, dialect: Dialect) -> bytes:
        return pickle.dumps(value)

    def process_result_value(self, value: bytes, dialect: Dialect) -> numpy.ndarray:
        return pickle.loads(value)

    def process_literal_param(self, value, dialect):
        raise NotImplementedError()

    @property
    def python_type(self):
        return numpy.ndarray
