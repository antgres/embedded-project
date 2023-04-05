from .baseModel import BaseModel, IdMixin, get_uuid, UndefinedKeyError
from ..bin.extensions import db
import json


def to_proc(json):
    """Create protocol object out of dict. Throw UndefinedKeyError if keys faulty."""
    try:
        name = json["name"]
        spec = json["specifications"]
        return Protocol(name, spec)
    except KeyError as e:
        raise UndefinedKeyError(e, "Protocol")


class Protocol(IdMixin, BaseModel):
    __tablename__ = "protocols"

    name = db.Column(db.String, nullable=False, unique=True)
    specifications = db.Column(db.String, nullable=False)
    schema = db.Column(db.Boolean, default=False)

    def __init__(self, name, specs, schema=False):
        """
        Create new Protocol out of give specifications.

        :param name: Name of the Protocol.
        :param specs: Specifications of the Protocol in type dict.
        :param schema: Flag if the Protocol is a schema.
        """
        self.name = name
        self.specifications = json.dumps(specs)
        self.schema = schema
        self.id = get_uuid()

    def serialize(self, no_id=False):
        """
        Return object data in easily serializable format.
        If parameter no_id=True, the id of the object gets added to the dict. Default: False.
        """
        d = {
            'name': self.name,
            'specifications': json.loads(self.specifications)
        }
        if not no_id:
            d["id"] = self.id

        return d

    def serialize_spec(self):
        """Load specifications from object in dict."""
        return json.loads(self.specifications)

