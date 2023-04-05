"""Custom global error messages."""

import datetime
from flask import json, Blueprint
from werkzeug.exceptions import *

blueprint = Blueprint('error_handler', __name__)


@blueprint.app_errorhandler(NotFound)
def not_found(e):
    response = e.get_response()
    response.content_type = "application/json"

    response.data = json.dumps({
        'status': e.code,
        "error": e.name,
        "message": e.description,
        "timestamp": datetime.datetime.now().astimezone().isoformat()
    })
    return response


@blueprint.app_errorhandler(BadRequest)
def bad_request(e):
    response = e.get_response()
    response.content_type = "application/json"

    response.data = json.dumps({
        'status': e.code,
        "error": e.name,
        "message": e.description.split(":")[-1],
        "timestamp": datetime.datetime.now().astimezone().isoformat()
    })
    return response


@blueprint.app_errorhandler(MethodNotAllowed)
def bad_request(e):
    response = e.get_response()
    response.content_type = "application/json"

    response.data = json.dumps({
        'status': e.code,
        "error": e.name,
        "message": e.description,
        "timestamp": datetime.datetime.now().astimezone().isoformat()
    })
    return response


@blueprint.app_errorhandler(InternalServerError)
def bad_request(e):
    response = e.get_response()
    response.content_type = "application/json"

    response.data = json.dumps({
        'status': e.code,
        "error": e.name,
        "message": e.description,
        "timestamp": datetime.datetime.now().astimezone().isoformat()
    })
    return response
