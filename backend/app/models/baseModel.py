from sqlalchemy.exc import IntegrityError
import datetime
import uuid
from ast import literal_eval
from ..bin.extensions import db


class UndefinedKeyError(Exception):
    """Custom error message to extract KeyError messages."""
    # Constructor or Initializer
    def __init__(self, e, model=""):
        msg = e.message if hasattr(e, 'message') else str(e)
        self.message = literal_eval(msg)
        self.model = model

    def __str__(self):
        msg = repr(self.message) if type(self.message) != str else self.message
        return f"'{self.model}.{msg}'" if self.model else msg


def get_uuid():
    """Build 32-char random hash"""
    return str(uuid.uuid4()).replace("-", "")


class IdMixin:
    """Mixin for database Column 'id'"""
    id = db.Column(db.String, primary_key=True, default=get_uuid())


class BaseModel(db.Model):
    """Base data model for all objects"""
    __abstract__ = True

    created_at = db.Column(db.String, default=lambda: datetime.datetime.now().astimezone().isoformat())

    def save_to_db(self):
        """Save object into database."""
        try:
            db.session.add(self)
            db.session.commit()
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
        finally:
            db.session.close()
