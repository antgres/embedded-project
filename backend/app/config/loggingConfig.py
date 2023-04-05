import logging
import time
import os
from logging.config import dictConfig

LOGGING_DIRECTORY = "log"


def create_logger(root_dir, logging_state):
    """Creates a custom logger with settings defined in LOGGING_SCHEMA."""
    global LOGGING_DIRECTORY
    LOGGING_DIRECTORY = f"{root_dir}/{LOGGING_DIRECTORY}"
    os.makedirs(LOGGING_DIRECTORY, exist_ok=True)

    # load LOGING_SCHEMA
    dictConfig(LOGGING_SCHEMA)

    # set logging.level depending on app.debug flag
    level = logging.DEBUG if logging_state else logging.ERROR
    logging.getLogger().setLevel(level)


LOGGING_SCHEMA = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        "colored": {
            "class": "coloredlogs.ColoredFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            "format": "%(asctime)s [%(levelname)s] %(name)s | Line %(lineno)d - %(message)s"
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s | Line %(lineno)d - %(message)s',
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        },

    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'colored',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'file_handler': {
            'level': 'ERROR',
            'filename': f"{LOGGING_DIRECTORY}/{time.strftime('%Y_%m_%d_%H_%M_%S')}.log",
            'class': 'logging.FileHandler',
            "delay": True,
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['file_handler', 'default'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
