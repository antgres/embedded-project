#!flask/bin/python
from os import getenv
from os.path import dirname
import sys

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from app.bin.check_protocols import check_available_protocols
from app.config.loggingConfig import create_logger

from logging import getLogger

log = getLogger()


def create_app():
    """Create and configure Flask application."""
    application = Flask(__name__)

    with application.app_context():
        ####### load config object #######
        load_dotenv()  # load .env file
        config_obj = getenv('USED_CONFIG')
        if config_obj:
            application.config.from_object("app.config.APP_Config." + config_obj)

            print(f" * Loaded config '{config_obj}'")
        else:
            exit(f"Not known Config object or Path '{config_obj}'")

        create_logger(dirname(__file__), application.debug)
        print(" * Created logger")

        ####### check python version #######
        if sys.version_info <= (3, 9):
            # check if used interpreter is <= ver.3.9
            log.warning("Your used Python interpreter is too old. Proceed at your own risk.")

        ####### create extensions instances #######
        from app.bin.extensions import db, scheduler

        db.init_app(application)
        db.app = application  # fix for APScheduler context

        # initialize schedule
        from app.bin import tasks  # initialize @scheduler for APScheduler
        scheduler.api_enabled = True
        scheduler.init_app(application)
        scheduler.start()

        # enable CORS
        CORS(application, resources={r'/*': {'origins': '*'}})
        print(" * CORS settings activated")

        ####### Register Blueprints #######
        from app.bin import errorHandler
        from app.apis import general, api_mqtt

        root = getenv("APPLICATION_ROOT")

        application.register_blueprint(errorHandler.blueprint, url_prefix=root)

        application.register_blueprint(general.blueprint, url_prefix=root)
        application.register_blueprint(api_mqtt.blueprint, url_prefix=root)

        print(" * Created all routes")

        db.create_all()
        print(" * Created Database")

        check_available_protocols()
        print(" * Added all schemas")

        return application


if __name__ == "__main__":
    # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
    create_app().run(host=getenv('APP_HOST_IP'), port=getenv('APP_PORT'), use_reloader=False, threaded=True)
