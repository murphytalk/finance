"""
The flask application package.
"""
from os import environ
from os.path import isfile
from platform import node
from flask import Flask
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.exceptions import NotFound

# check hostname to determine if it is a production deployment
deployed_in_production = node() == "anchor"

DEBUG = not deployed_in_production

env_db = environ.get('FINANCE_DB')
if env_db is None or (not isfile(env_db)):
    DATABASE = None  # FakeDao will be used
else:
    DATABASE = env_db

# deployed behind ngix
URL_ROOT = ("/finance" if DATABASE is not None else "/finance_demo") if deployed_in_production else None

app = Flask(__name__)
# load all uppercase variables ad configuration
app.config.from_object(__name__)
app.debug = DEBUG

if URL_ROOT is not None:
    app.config["APPLICATION_ROOT"] = URL_ROOT
    application = DispatcherMiddleware(NotFound, {URL_ROOT: app})
else:
    application = app

from finance import views
