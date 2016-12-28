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
# deployed behind ngix
URL_ROOT = "/finance" if deployed_in_production else None

env_db = environ.get('FINANCE_DB')
DATABASE = r"E:\work\finance\finance.db" if env_db is None else env_db
if not isfile(DATABASE):
    DATABASE = None  # FakeDao will be used

app = Flask(__name__)
# load all uppercase variables ad configuration
app.config.from_object(__name__)
app.debug = DEBUG

if URL_ROOT is not None:
    app.config["APPLICATION_ROOT"] = URL_ROOT
    application = DispatcherMiddleware(NotFound, {URL_ROOT: app})
else:
    application = app

import views
