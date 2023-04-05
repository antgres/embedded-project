import json
from ast import literal_eval

from app.bin.helper_functions import check_last_character


def modify_spec(string):
    """Modifies the last char of dict["main_topic]."""
    d = json.loads(string)
    d["main_topic"] = check_last_character(d["main_topic"])
    return json.dumps(d)


class MQTT_DATA:
    def __init__(self, id: str, name: str, value, unit: str, topic: str, proc_name: str):
        self.sensor_id = id
        self.sensor_name = name
        self.sensor_value = self._check_value(value)
        self.sensor_unit = unit
        self.topic = "".join(topic[:-1].rpartition("/")[:-1])  # cut off subtopic, only main_topic
        self.proc_name = proc_name

    def _check_value(self, value):
        """Check if value is of type str and if so convert it to type int/float"""
        value = literal_eval(value) if isinstance(value, str) else value
        return value if isinstance(value, int) else format(value, '.2f')

    def _serialize_info(self):
        """Create a string out of the additional saved information about the data."""
        return json.dumps({
            'sensor_id': self.sensor_id,
            'sensor_name': self.sensor_name,
            'sensor_topic': self.topic
        })

    def get_proc_name(self):
        return self.proc_name

    def get_value_unit_info(self):
        return self.sensor_value, self.sensor_unit, self._serialize_info()
