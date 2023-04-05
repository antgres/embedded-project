import json

from .baseModel import BaseModel, UndefinedKeyError
from .pairsModel import Pairs
from .protocolModel import Protocol
from ..bin.extensions import db


def to_data(json):
    """Create data object out of dict. Throw UndefinedKeyError if keys faulty."""
    try:
        hash = json["pair_hash"]
        value = json["value"]
        unit = json["unit"]
        proc_name = json["protocol_name"]
        return Data(value, unit, hash, proc_name)
    except KeyError as e:
        raise UndefinedKeyError(e, "Data")


class Data(BaseModel):
    __tablename__ = "data"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    value = db.Column(db.Float(precision=2), nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    further_info = db.Column(db.String, default="")

    protocol_name = db.Column(db.String, db.ForeignKey(Protocol.name))
    pair_hash = db.Column(db.String, db.ForeignKey(Pairs.hash))

    def __init__(self, value, unit: str, pair_hash, proc_name: str, info=""):
        """
        Create data object from a sensor.

        :param value: Value of the Sensor.
        :param unit: Unit of the value, eg 'percent', 'kg', 'kg*m/s^2'
        :param pair_hash: Hash of the pair from which the sensor value originates.
        :param proc_name: Protocol name used to communicate with the pair.
        :param info: Further Information from type dict.
        """
        self.value = value
        self.unit = unit
        self.further_info = info
        self.pair_hash = pair_hash
        self.protocol_name = proc_name

    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'pair_hash': self.pair_hash,
            'value': self.value,
            'unit': self.unit,
            'further_info': self._add_to_further_infos(),
            'created_at': self.created_at
        }

    def _add_to_further_infos(self):
        """Store further variables in Column further_info"""
        d = json.loads(self.further_info)
        d["protocol_name"] = self.protocol_name
        return d
