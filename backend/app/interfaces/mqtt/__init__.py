import paho.mqtt.client as mqtt
from time import sleep, time
from enum import Enum, auto

from app.bin.helper_functions import check_last_character
from .mqtt_bin import MQTT_DATA


def run_interface(_dict):
    """
    Entry point for the MQTT interface. Function deserializes _dict = pair.serialize() and sends a MQTT message
    to the device. The device sends all his sensor data back which is stored in class MQTT_Data.

    :param _dict: a dict from pair.serialize()
    :returns: pair_hash, error_message, list(MQTTData) or None
    """
    ## get values from _dict
    hash = _dict.get("hash")  # get pair.hash

    proc = _dict.get("protocol")  # get dict(protocol)
    proc_name, specs = proc.get("name"), proc.get("specifications")
    broker, topic = specs["broker"], specs["main_topic"]

    data = None
    message = ""

    try:
        # send message to pair with subtopic 'data_all'
        (topic, msg) = MQTT(broker=broker, main_topic=topic).send_message(subtopic="data_all")

        if not topic:
            # if topic == None -> No connection possible due to other errors
            raise Exception("No connection to device.")

        # convert list(list(str)) to list(obj(MQTT_Data))
        data = [MQTT_DATA(id, name, value, unit, topic, proc_name) for id, name, value, unit in msg]
    except Exception as e:
        # save error message
        message = str(e)

    return hash, message, data


class MQTT:
    """
    Send one message to device, wait for one message and disconnect.

    """

    class States(Enum):
        """States which the communication can be."""
        NOT_DEFINED = auto()
        IDLE = auto()
        SEND = auto()
        RECEIVED = auto()
        DISCONNECTED = auto()

    # After self.TIMEOUT seconds the published message is considered lost
    TIMEOUT = 7

    SEP_SYMBOL, END_SYMBOL, DIV_SYMBOL = "=", "#", "§"

    def __init__(self, broker: str, main_topic: str, port=1883, debug=False, not_connect=True):
        """

        :param broker:
        :param main_topic:
        :param port:
        :param debug:
        :param not_connect:
        """
        # initialize variables
        self.status = self.States.NOT_DEFINED

        self.og_topic = "".join(check_last_character(main_topic))
        self.broker, self.debug, self.port = broker, debug, port
        self.not_connect = not_connect

        # create client
        self._create_client()
        self.status = self.States.IDLE

    def send_message(self, subtopic: str, message="", qos=0, disconnect_after=True):
        """
        Send message to subtopic.

        :param subtopic:
        :param message:
        :param qos:
        :param disconnect_after:
        :return:
        """

        # build new topic to receive data on
        new_top = "".join(check_last_character([self.og_topic, subtopic]))

        if new_top != self.client.topic:
            # if not the same, resubscribe
            check = self._sub_new_to_topic(new_top)

            if not check:
                raise Exception("Error with resubscription")

        if message:
            # if a message is given
            message = self._build_message(message)

        try:
            return self._send_message(message, qos, disconnect_after)
        except Exception as e:
            self._disconnect()
            return None, str(e)

    def _send_message(self, msg, qos, disconnect_after):
        """

        :return:
        """
        if not self.client.connected_flag:
            # if client not connected
            raise Exception("No connection")

        # build topic to publish message on
        main_topic, _, subtopic = self.client.topic[:-1].rpartition("/")  # split topic
        main_topic += _  # add "/" to main_topic

        # build custom message
        msg = f"{subtopic}{self.DIV_SYMBOL}{msg}"

        # save original published message for use in _on_message()
        self.client.msg = msg

        # https://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels/
        # https://www.hivemq.com/blog/mqtt-essentials-part-8-retained-messages/
        info = self.client.publish(main_topic, msg, qos=qos, retain=False)

        self.status = self.States.SEND
        if self.debug: f"send message '{msg}' on topic '{self.client.topic}'"

        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            # if no successful connection
            raise Exception("Connected but no message send")

        end_time = time() + self.TIMEOUT

        while self.status != self.States.RECEIVED:
            # wait for message to arrive if status not received
            if time() > end_time:
                # if no message after TIMEOUT received throw exception
                raise Exception("No connection after message send")

        if disconnect_after:
            self._disconnect()

        return self._decode_message()

    def _decode_message(self):
        """
        Decode custom message.

        """
        topic, msg = self.client.topic, self.client.msg

        # split msg into parts
        messages = [x for x in msg.split(self.END_SYMBOL) if x]
        # check messages if custom msg from device included
        found_custom_msg = bool(len([e for e in messages if self.SEP_SYMBOL in e]))

        if not found_custom_msg:
            # if custom msg not included
            return topic, messages

        return topic, [x.split(self.SEP_SYMBOL) for x in messages]

    def _build_message(self, msg):
        # for future use
        return msg

    def _create_client(self):
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)  # look up mqtt.Client documentation

        self.client.connected_flag = False  # define custom flag in class

        self.client.topic = self.og_topic  # save main_topic in client
        self.client.msg = ""  # initialize client.msg

        # http://www.steves-internet-guide.com/mqtt-python-callbacks/
        self.client.on_connect = self._on_connect  # callback: establishing connection
        self.client.on_message = self._on_message  # callback: receiving message on subscribed topic
        self.client.on_disconnect = self._on_disconnect  # callback: client disconnects
        self.client.on_unsubscribe = self._on_unsubscribe  # callback: client unsubscribes topic
        self.client.on_subscribe = self._on_subscribe  # callback: client subscribes topic

        try:
            self.client.connect(host=self.broker, port=self.port, keepalive=40)
            self.client.loop_start()  # asynchronous loop
        except OSError:
            raise Exception("Can´t connect to device. Look up if in same network as broker.")

        sleep(1)  # wait for callback _on_connect to happen (for connected_flag)

    def _sub_new_to_topic(self, new_top):
        """
        Resubscribe to topic

        :param new_top:
        :return:
        """
        if not self.not_connect:
            info = self.client.unsubscribe(self.client.topic)
            self.not_connect = True

            if info[0] != mqtt.MQTT_ERR_SUCCESS:
                return False

        self.client.topic = new_top
        info = self.client.subscribe(new_top)
        return info[0] == mqtt.MQTT_ERR_SUCCESS

    # The callback for when the client receives a CONNACK response from the server.
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.connected_flag = True  # set flag
        else:
            print("Bad connection. Returned code = ", rc)

        # Subscribe to topic on which the server listens to incoming messages.
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        if not self.not_connect:
            self.client.subscribe(client.topic)
            if self.debug: f"subscribed to topic '{client.topic}'"

    def _on_message(self, client, userdata, msg):
        """
        Save message in client.
        """
        # split data into necessary parts
        send_topic = msg.topic
        msg = msg.payload.decode('utf-8')

        if msg == client.msg and send_topic == client.topic:
            # ignore same message as send
            return

        if self.debug: f"received message: {msg} (on topic {send_topic})"

        self.client.msg = msg
        self.status = self.States.RECEIVED

    def _on_unsubscribe(self, client, userdata, mid):
        if self.debug: print(f"Unsubscribed from {client.topic}")

    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        if self.debug: print(f"Subscribed to {client.topic}")

    def _on_disconnect(self, client, userdata, rc):
        if self.debug: print(f"Disconnected from {client.topic}")

        # logging.info("disconnecting reason  "  +str(rc))
        self.client.connected_flag = False

    # Disconnect client
    def _disconnect(self):
        self.client.loop_stop()  # Stop loop
        self.client.disconnect()  # disconnect
        self.status = self.States.DISCONNECTED
        if self.debug: f"disconnected"
