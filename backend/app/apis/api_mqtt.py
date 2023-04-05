from sqlalchemy import and_
from flask import jsonify, abort, request, Blueprint

from ..bin.helper_functions import unpack, create_pair_dict, unpack_tuple_list
from ..models.pairsModel import Pairs, to_pair
from ..models.protocolModel import Protocol, to_proc
from ..models.baseModel import UndefinedKeyError

from ..interfaces.mqtt import MQTT
from ..interfaces.mqtt.mqtt_bin import modify_spec

blueprint = Blueprint('api_mqtt', __name__)


## Example:
# {
#     "name": "Love_Ship_1",
#     "protocol": {
# 			"name": "MQTT",
# 			"specifications": {
# 				"broker": "192.168.4.1",
# 				"main_topic": "garden/lab/"
# 			}
# 		}
# }
@blueprint.route('/addPairMQTT', methods=["POST"])
def add_pair():
    """
    Add a pair or update a disconnected pair to the database. System checks if the pair is already in the database.

    :returns: Returns a dict {success: bool, message: str}.
    If successful 'success: True' else {'success': False, 'message': 'ErrorMessage'}
    """
    data = request.json

    try:
        # create object protocol (check for keys)
        new_proc = to_proc(data["protocol"])

        # check value of key 'main_topic' for last char with function 'check_last_character'.
        # Reason: To avoid a duplicate db entry in the next Protocol.query if lazy user input
        new_proc.specifications = modify_spec(new_proc.specifications)

        # check if protocol with protocol.specs already defined
        proc_list = Protocol.query.filter_by(specifications=new_proc.specifications).all()
        if not proc_list:
            # if not, save as new
            temp_proc = new_proc.serialize()  # serialize data before data overwritten from save_to_db
            new_proc.save_to_db()
        elif len(proc_list) == 1:
            # if already defined serialize found proc.specifications
            temp_proc = unpack(proc_list).serialize()
        else:
            # if more than one entry was found, raise error
            raise Exception("More than one corresponding Protocol entry was found. Check database.")

        # create new pair instance with new hash
        pair = to_pair(data, temp_proc.get("id"))

        # search for pairs in db with same protocol.id and pair.name
        pair_query = Pairs.query.filter(
            and_(
                Pairs.protocol_id == pair.protocol_id,
                Pairs.name == pair.name
            )).all()

        # check how many pairs were found
        if len(pair_query) <= 1:
            # if no pair/one pair is existing with this attributes
            rectivate_flag = False  # flag for device which is in db but with status=False

            if len(pair_query) == 1:
                # if exactly one, pair already exists
                if unpack(pair_query).status:
                    # if status flag is True - Already defined and still connected
                    return jsonify({"success": True, "message": "Already defined."})

                # status flag is False - check for connection
                rectivate_flag, pair = True, unpack(pair_query)
                specs = pair.protocol.serialize_spec()
            else:
                # no pair found, specified data in json will be taken
                specs = temp_proc["specifications"]

            broker, topic = specs["broker"], specs["main_topic"]

            # check for MQTT connection with subtopic 'hash'
            (topic, msg) = MQTT(broker=broker, main_topic=topic) \
                .send_message(subtopic="hash", message=pair.hash)

            # check if connection success
            if not topic:
                # if topic == None -> No connection possible due to other errors
                return jsonify({"success": False, "message": f"No connection to device possible. Cause: {msg}"})

            if "success" not in msg:
                # Connection successful but internal error in device
                return jsonify({"success": False, "message": "Internal error. Check device."})

            # if success then connection happened, save success to db
            pair.update_status()
            if rectivate_flag:
                # pair existed and status flag got updated
                return jsonify({"success": True, "message": "Already defined. Reactivated status"})

            # new device
            return jsonify({"success": True, "message": ""})

        # if more than one entry was found, raise error
        raise Exception("More than one corresponding Pairs entry was found. Try with new parameters.")
    except (KeyError, UndefinedKeyError) as e:
        abort(400, f"Wrong Key name {str(e)} specified")
    except Exception as e:
        abort(500, str(e))


@blueprint.route('/getAllActuatorMQTT/<pair_hash>', methods=["GET"])
def get_all_protocols(pair_hash):
    """
    Get all Actuator information from the specified pair_hash which can be found out through the route '/getAllPairs'.

    :returns: dict of {success: bool}.
    If successful additional key {actuators: list[dict]} added.
    If failure additional key {message: ErrorMessage} added.
    """
    try:
        # filter for pair.hash in db
        pair = Pairs.query.filter_by(hash=pair_hash).first()

        specs = pair.protocol.serialize_spec()
        broker, topic = specs["broker"], specs["main_topic"]

        # send mqtt message
        (topic, msg) = MQTT(broker=broker, main_topic=topic).send_message(subtopic="actuator_all")

        if not topic:
            # if topic == None -> No connection possible due to other errors
            return jsonify({"success": False, "message": 'Internal Error:' + msg})

        if msg:
            # message successfully send, create list(dict) out of variables
            msg_dict = [{
                "id": msg_list[0],
                "name": msg_list[1],
                "variables": create_pair_dict(msg_list[2:]),
            } for msg_list in msg]

            return jsonify({"success": True, "actuator": msg_dict})

        # Everything got wrong
        abort(500, msg)

    except (KeyError, UndefinedKeyError) as e:
        abort(400, f"Wrong Key name {str(e)} specified")
    except Exception as e:
        abort(500, str(e))


## Example
# {
#     "hash": "a0c55a71e68442db8927d159566758a6",
#     "actuator_id": "0",
#     "variables": {
#       "change_direction": "True",
#       "duty": "80"
#     }
# }
@blueprint.route('/setActuatorMQTT', methods=["POST"])
def set_actuator():
    """
    Sets the specified actuator from the Pair.hash with the specified variables.

    :returns: dict of {success: bool}.
    If successful additional key {"actuator_id": int, "values": list} added.
    If failure additional key {message: ErrorMessage} added.
    """
    data = request.json
    try:
        pair = Pairs.query.filter_by(hash=data["hash"]).first()

        # unpack values
        specs = pair.protocol.serialize_spec()
        broker, topic = specs["broker"], specs["main_topic"]
        id, var = data["actuator_id"], data["variables"]

        # build custom message out of data["variables"]
        # Example: {"change_direction": "True", "duty": "80"} -> "change_direction=True=duty=80"
        msg = f"{id}={'='.join(unpack_tuple_list([(k, v) for k, v in var.items()]))}"

        # send message
        (topic, msg) = MQTT(broker=broker, main_topic=topic) \
            .send_message(subtopic="set_actuator", message=msg)

        # unpack received custom msg
        a_id, value = unpack(msg, 1)

        if topic:
            return jsonify({"success": True, "actuator_id": a_id, "values": value})
        else:
            # if topic == None -> No connection possible due to other errors
            return jsonify({"success": False, "message": 'Internal Error:' + msg})

    except (KeyError, UndefinedKeyError) as e:
        abort(400, f"Wrong Key name {str(e)} specified")
    except Exception as e:
        abort(500, str(e))
