from collections import Counter
from os import getcwd, listdir
from os.path import isdir, join

# re.search("schema", x.protocol.name, re.IGNORECASE)

# global counter to count the number of disconnects of successfully connected pairs
PAIRS_LIST = Counter()


def create_interface_list(pair_list):
    """Creates a dict of {custom_path_to_directory_interface: pair}."""
    # get all directory names in root
    root = f"{getcwd()}/app/interfaces"

    # dict of {directory_name.lower(): directory_name}
    # because as it is not known how pair.protocol.name and directory_name are written
    available_interfaces = {item.lower(): item for item in listdir(root) if isdir(join(root, item))}

    # create dict of {custom_path_to_directory_interface: pair} if pair.protocol.name.lower() is in available_interfaces
    return {f"app.interfaces.{available_interfaces.get(pair.protocol.name.lower())}": pair
            for pair in pair_list if pair.protocol.name.lower() in available_interfaces}
