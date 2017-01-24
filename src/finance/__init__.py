"""
The flask application package.
"""
from os import environ
from os.path import isfile
from platform import node
from flask import Flask, Blueprint
from finance import settings
from finance.api import api
from finance.api.endpoints.report import ns as api_reports


def configure_app(flask_app):
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


# check hostname to determine if it is a production deployment
deployed_in_production = node() == "anchor"

DEBUG = not deployed_in_production

env_db = environ.get('FINANCE_DB')
if env_db is None or (not isfile(env_db)):
    DATABASE = None  # FakeDao will be used
else:
    DATABASE = env_db

# deployed behind ngix
URL_ROOT = ("/finance" if DATABASE is not None else "/finance_demo")


app = Flask(__name__)
# load all uppercase variables ad configuration
app.config.from_object(__name__)
app.debug = DEBUG

configure_app(app)

finance_page = Blueprint('finance_page', __name__, url_prefix=URL_ROOT)
from finance import views
# need to register after all URLS are defined in views
app.register_blueprint(finance_page)

api_page = Blueprint('api', __name__, url_prefix='/api')
api.init_app(api_page)
api.add_namespace(api_reports)
app.register_blueprint(api_page)
