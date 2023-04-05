from mcp3008 import MCP3008


# sensors output: value, unit
def get_poti_data(data):
    necessary_data = ['__class', "channel"]

    adc, channel = [data.get(k) for k in necessary_data]
    return adc.read(channel=channel)


def init_all_sensors():
    # id, name, f, input_for_f
    LIST = []

    # appened sensor Poti
    LIST.append(
        (0, "Potentiometer", get_poti_data, {"__class": MCP3008(), "channel": 0})
    )

    return LIST
