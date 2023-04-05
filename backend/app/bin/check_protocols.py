from os.path import dirname
from sqlalchemy import or_
from logging import getLogger
import json

from app.models.protocolModel import Protocol, to_proc
from .extensions import db

log = getLogger()


def check_available_protocols():
    """
    Adds all Protocol_SCHEMAS defined  in 'available_protocols.json' to database. If all SCHEMAS are already defined
    in database no new SCHEMA is saved in database. Deletes SCHEMAS which are not defined in available_protocols.json
    out of the database.
    """
    try:
        with open(f"{dirname(dirname(__file__))}/config/available_protocols.json", "r") as f:
            # load all schemas
            defined_procs = json.load(f)

        # if schemas defined
        if defined_procs:
            # build obj(protocol) out of loaded schemas
            proc_list = [to_proc(x) for x in defined_procs]

            # filter for protocols in database with SCHEMA properties
            found_procs = Protocol.query.filter(
                or_(
                    Protocol.name.contains("SCHEMA"),
                    Protocol.schema == True
                ))

            if found_procs:
                # if schemas were found in database
                values_defined = [x.get("name") for x in defined_procs]  # get schema_name from file
                values_found = [x.name for x in found_procs]  # get schema_name from query

                if values_found == values_defined:
                    # schemas in db are equal to schemas in file
                    return

                found = False
                for f in found_procs:
                    if f.name not in values_defined:
                        # delete entries in db which are not defined anymore
                        Protocol.query.filter_by(name=f.name).delete()
                        found = True

                if found:
                    # if entries got deleted
                    print(" * DELETED OLD SCHEMAS")
                    db.session.commit()  # save changes

                found = False
                for d in proc_list:
                    if d.name not in values_found:
                        # save entries which are not in db
                        d.save_to_db()
                        found = True

                if found:
                    # if entries got saved
                    print(" * ADDED NEW SCHEMAS")

            else:
                # if no schemas are defined in the db, save all schemas in file to db
                for proc in proc_list:
                    proc.save_to_db()

                print(" * ADDED NEW SCHEMAS")

        else:
            log.error("No defined Protocol_SCHEMAS found. Add SCHEMAS.")
            exit("No defined Protocol_SCHEMAS found. Add SCHEMAS.")

    except IOError:
        # File could not be opened
        log.error("File available_protocols.json could not be opened")
        exit("File available_protocols.json could not be opened")
    except (KeyError, Exception) as e:
        log.error(str(e))
        exit(e)
