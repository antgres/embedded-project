from sqlalchemy.orm import relationship, backref
from .baseModel import BaseModel, get_uuid, UndefinedKeyError
from .protocolModel import Protocol
from ..bin.extensions import db


def to_pair(json, proc_id):
    """Create pair object out of dict. Throw UndefinedKeyError if keys faulty."""
    try:
        name = json["name"]
        return Pairs(name, proc_id)
    except KeyError as e:
        raise UndefinedKeyError(e, "Pairs")


class Pairs(BaseModel):
    __tablename__ = "pairs"

    name = db.Column(db.String(24), nullable=False)
    hash = db.Column(db.String(36), primary_key=True)

    protocol_id = db.Column(db.String, db.ForeignKey(Protocol.id))
    protocol = relationship("Protocol", backref=backref("Pairs", lazy="joined"))

    status = db.Column(db.Boolean, nullable=False, default=False)

    data = relationship("Data")

    def __init__(self, name, proc_id):
        """
        Create Pair object with new hash.

        :param name: Name of the Pair.
        :param proc_id: Id of the used protocol.
        """
        self.name = name
        self.protocol_id = proc_id
        self.hash = get_uuid()
        self.status = False

    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name': self.name,
            'hash': self.hash,
            'protocol': self.protocol.serialize(),
            'status': self.status
        }

    def update_status(self):
        """Update status Flag of object in database"""
        self.status = not self.status
        self.save_to_db()
