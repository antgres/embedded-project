# Seperator Symbol for all Messages
SEP_SYMBOL, END_SYMBOL = "=", "#"

def create_message(keys):
    # convert values in str
    for index, value in enumerate(keys):
        keys[index] = str(value)

    # join keys together as defined
    return SEP_SYMBOL.join(keys) + END_SYMBOL

def update_actuator_values(data_str, a_data):
    lst = data_str.split(SEP_SYMBOL)
    
    n, data = 2, {} # batch size
    for i in range(0, len(lst)-1, n):
        key, value = lst[i:i+n]
        data[key] = type(a_data[key])(value)
        
    a_data.update(data)
    return a_data
    