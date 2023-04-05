from os.path import dirname

# A secret key that will be used for securely signing the session cookie and can be used for any other security
# related needs by extensions or your application. It should be a long random string of bytes, although unicode is
# accepted too.
SECRET_KEY = r"7ZXyM8ch7Rrd8CPnHYawPbG1DIWgb0dYWUQVKnrM3CruLw2n1sgSPv" \
             r"/040Hj2bNgpAYQ4ylPb9GPTgWH6TrtToI79J8t6KwL5jA6MYRFTJCSw" \
             r"hlxampl1fDL1PyO5nIK6zV6F5wO2dv2mAhuromCyfDTMu6v01FoqH0dXYJnCo0= "


class BaseConfig(object):
    """Set Flask config variables."""
    DEVELOPMENT = False
    DEBUG = False
    FLASK_SECRET = SECRET_KEY
    # When set to True protects from Cross-Site Request Forgery
    CSRF_ENABLED = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # will track modifications of objects and emit signals
    SQLALCHEMY_ECHO = False  # log all SQL calls

    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#connection-uri-format
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{dirname(dirname(__file__))}/database.db"


################################################

class DevConfig(BaseConfig):
    """Development configurations"""
    FLASK_ENV = 'development'
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProdConfig(BaseConfig):
    """Production configurations"""
    FLASK_ENV = 'production'
