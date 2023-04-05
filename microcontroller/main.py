from bin import create_message

# decode binary_str to str
_topic_str = subscription_topic.decode('utf-8')
# check if last char '/', else add '/'
topic_str = _topic_str  if _topic_str[-1] == "/" else "{}/".format(_topic_str)
# global variables
NEW_MESSAGE = []


def get_all_data():
    global sensor_list

    msg = ""
    for s_id, name, func, s_data in sensor_list:
        value, unit = func(s_data)
        msg += create_message([s_id, name, value, unit])

    return msg


def get_actuator_info():
    global actuator_list

    msg = ""
    for index, value in enumerate(actuator_list):
        name, _, a_data = value
        
        # get all keys which are not private (private keys with "__" in name)
        _keys_list = [(keys, type(value).__name__) for keys, value in a_data.items() if "__" not in keys]
        keys_list = [item for t in _keys_list for item in t] # unpack list of tuple into list
        
        msg += create_message([index, name] + keys_list)

    return msg


def set_actuator(message):
    global actuator_list
    from bin import SEP_SYMBOL, update_actuator_values
    
    # get data out of message
    wish_id, _, data = message.partition(SEP_SYMBOL)
    
    for index, value in enumerate(actuator_list):
        if index == int(wish_id):
            # update and save values
            _, func, a_data = value # get values
            a_data = update_actuator_values(data, a_data) # update values
            actuator_list[index] = _, func, a_data # save values 
        
            
            try:
                result = func(a_data)
                msg = "success" if not result else result
                
                return create_message([index, msg])
            except Exception as e:
                return create_message([index, "internal_error"])                
            
    # if no actuator was found with wished for id
    return create_message([wish_id, "not_found"])



def check_hash_file(msg):
    file = "hash.txt"

    try:
        uos.stat(file)  # check if file exists

        with open(file, "r") as f:
            data = f.readlines()

        if data == msg:
            # wenn gleicher Wert
            return True
    except Exception:
        pass

    try:
        with open(file, "w+") as f:
            f.write(msg)
    except IOError:
        return False

    return True


def callback(topic, msg):
    global topic_str, NEW_MESSAGE

    # encode binary string to string
    msg = msg.decode('utf-8')

    if "§" in msg:
        # message encoded
        subtopic, msg = msg.split("§")
    else:
        # no message encoded in msg, only subtopic
        subtopic = msg

    # topics
    new_msg, text = "error", "<- New inquiry:"
    if subtopic == "hash":
        print("{} Hash {}".format(text, msg))

        result = check_hash_file(msg)
        new_msg = "success" if result else "failure"

    if subtopic == "data_all":
        print("{} Get all data".format(text))
        new_msg = get_all_data()

    if subtopic == "actuator_all":
        print("{} Get all actuator id`s".format(text))
        new_msg = get_actuator_info()

    if subtopic == "set_actuator":
        print("{} Set actuator to {}".format(text, msg))
        new_msg = set_actuator(msg)

    new_topic = "{}{}/".format(topic_str, subtopic)

    NEW_MESSAGE.append((new_topic, new_msg))


def on_connect():
    global client_id, mqtt_broker, topic_str
    
    
    client = MQTTClient(client_id, mqtt_broker)
    client.set_callback(callback)

    client.connect()
    client.subscribe(topic_str)
    print('Connected to {} MQTT broker, subscribed to topic: {}'.format(mqtt_broker, topic_str))

    return client


def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(5)
    machine.reset()


def send_message(topic, message):
    client.publish(topic, message.encode('utf-8')) # check if correct
    

if __name__ == "__main__":
    
    # start connection
    try:
        client = on_connect()
    except OSError as e:
        restart_and_reconnect()

    i = 0
    disconnect = False
    
    ## test
    #print(get_all_data())
    #print(get_actuator_info())
    #print(set_actuator("0=duty=80=change_direction=False"))

    while True:
        try:
            # check for new messages
            client.check_msg()

            if NEW_MESSAGE:
                for topic, msg in NEW_MESSAGE:
                    print("-> send message '{}' on topic '{}'".format(msg, topic))
                    i += 1
                    print(i) # log

                    send_message(topic, msg)

                    if "hash" in msg.split("§"):
                        disconnect = True

                NEW_MESSAGE = []

                if disconnect:
                    client.disconnect()

        except OSError as e:
            restart_and_reconnect()
        except Exception as e:
            print(e)
            pass
