from flask import Blueprint, jsonify, request, abort
from sqlalchemy import not_

from ..models.dataModel import Data
from ..models.pairsModel import Pairs
from ..models.protocolModel import Protocol

blueprint = Blueprint('general', __name__)


@blueprint.route('/', methods=['GET'])
def get_ping():
    return jsonify(success=True)


@blueprint.route('/getAllSchemas', methods=["GET"])
def get_all_protocol_schemas():
    found_procs = Protocol.query.filter(Protocol.name.contains("SCHEMA"))
    return jsonify([x.serialize(no_id=True) for x in found_procs]) if found_procs else jsonify([])


# /getAllProtocols/086badea80ee4b8ea4b83d79d5835d5b
@blueprint.route('/getAllProtocols/', methods=["GET"])
@blueprint.route('/getAllProtocols/<proc_id>', methods=["GET"])
def get_all_protocols(proc_id=None):
    if not proc_id:
        # if no proc provided get all procs
        proc_list = Protocol.query.filter(
            not_(Protocol.name.contains("SCHEMA"))
        )
    else:
        # if id get proc from id
        proc_list = Protocol.query.filter_by(id=proc_id).all()

    return jsonify([x.serialize() for x in proc_list]) if proc_list else jsonify([])


@blueprint.route('/getAllPairs', methods=["GET"])
def get_all_pairs():
    pairs_list = Pairs.query.all()
    return jsonify([x.serialize() for x in pairs_list]) if pairs_list else jsonify([])


# /getPairsData/a0c55a71e68442db8927d159566758a6
@blueprint.route('/getPairsData/', methods=["GET"])
@blueprint.route('/getPairsData/<hash>', methods=["GET"])
def get_all_data_pairs(hash=None):
    if not hash:
        # if no hash provided get all data
        data_list = Data.query.all()
    else:
        # if hash get all data from hash
        data_list = Data.query.filter_by(pair_hash=hash).all()

    return jsonify([x.serialize() for x in data_list]) if data_list else jsonify([])
