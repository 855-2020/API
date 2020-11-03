"""
Dependencies used by the main api
"""
from .database import SessionLocal


def get_db():
    """
    Returns a new DB instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # pylint: disable=no-member
