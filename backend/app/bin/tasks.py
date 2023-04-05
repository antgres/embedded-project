import importlib
from logging import getLogger
from concurrent.futures import ThreadPoolExecutor, as_completed

from .extensions import scheduler
from ..models.pairsModel import Pairs
from ..models.dataModel import Data
from .tasks_bin import PAIRS_LIST, create_interface_list

log = getLogger()


@scheduler.task('interval', id='getDataFromAllInterfaces', seconds=10, max_instances=1)
def get_all_data_from_interfaces():
    """
    Send requests to the active pairs in intervals to enter all their sensor data into the database.
    Each request is threaded. Only pairs that have (pair.status = True) are taken into account.

    Each interface has a function 'run_interface' which executes the communication in the described protocol to the
    pair. It receives pairs.serialize() as input. From the function one receives the hash of the pair,
    an error_message if an internal error occurred and list(class CustomData).

    If a pair collects 4 disconnects, its status is set to False in the database.
    """
    # search for all Pairs with active flag
    pair_list = [x for x in Pairs.query.all() if x.status is True]

    if pair_list:
        # if pairs were found create thread pool out of pairs
        with ThreadPoolExecutor() as executor:
            # create dict of {path_to_interface: pair}
            interface_list = create_interface_list(pair_list)

            futures = {}
            for func_name, pair in interface_list.items():
                # create dict of {futures: pair}
                try:
                    # add {future: pair} to futures
                    # advantage: If a {future: pair} can not be added, the remaining could be added.
                    futures.update({executor.submit(
                        # get function 'run_interface' defined in the interface with input pair.serialize()
                        getattr(importlib.import_module(func_name), "run_interface"), pair.serialize()): pair})
                except Exception as e:
                    log.error(f"Pair with hash {pair.hash} on interface_name {func_name} throws {e}")

            # for returned futures
            for future in as_completed(futures):
                try:
                    hash, err_msg, datas = future.result()
                except Exception as e:
                    log.error(f"{futures[future]} throws {e}")
                else:
                    if datas:
                        # When data is received successfully set counter to zero for hash
                        PAIRS_LIST[hash] = 0

                        # save data to db
                        for data in datas:
                            value, unit, info = data.get_value_unit_info()
                            Data(value, unit, hash, data.get_proc_name(), info).save_to_db()
                    else:
                        # Not data received -> internal error in device or function
                        log.error(f"Error: '{err_msg}' for hash {hash}")
                        if PAIRS_LIST.get(hash):
                            # if already in list add 1
                            PAIRS_LIST[hash] += 1
                        else:
                            # if new in list start with 1
                            PAIRS_LIST[hash] = 1
    else:
        # if no pairs were found add +1 to every key in PAIRS_LIST
        PAIRS_LIST.update(PAIRS_LIST.keys())

    # change status flag of pair after 4 disconnects
    hash_list = [key for key, value in PAIRS_LIST.items() if value > 3]

    for pair_hash in hash_list:
        # if pair got 4 disconnects look up hash in db
        del_pair = Pairs.query.filter_by(hash=pair_hash).first()
        # update status to inactive, save and delete hash entry in PAIRS_LIST
        del_pair.update_status()
        del PAIRS_LIST[pair_hash]

        log.info(f"For pair with hash {pair_hash} set status to False")
