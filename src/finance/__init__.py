"""
The flask application package.
"""
from os import environ
from os.path import isfile
from platform import node
from flask import Flask, Blueprint
from finance.api import api
from finance.api.endpoints.report import ns as api_reports
from finance.api.endpoints.reference import ns as api_reference
from finance.api.endpoints.instrument import ns as api_instrument
from finance.api.endpoints.transaction import ns as api_transaction


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

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False
SWAGGER_UI_JSONEDITOR = True

app = Flask(__name__)
# load all uppercase variables as configuration
app.config.from_object(__name__)
app.debug = DEBUG

finance_page = Blueprint('finance_page', __name__, url_prefix=URL_ROOT)
from finance import views
# need to register after all URLS are defined in views
app.register_blueprint(finance_page)

api_page = Blueprint('api', __name__, url_prefix='%s/api' % URL_ROOT)
api.init_app(api_page)
api.add_namespace(api_reports)
api.add_namespace(api_reference)
api.add_namespace(api_instrument)
api.add_namespace(api_transaction)
app.register_blueprint(api_page)

