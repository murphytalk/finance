"""
The flask application package.
"""
from os import environ
from os.path import isfile
from platform import node
from flask import Flask
from werkzeug.wsgi import DispatcherMiddleware

URL_ROOT = "/finance"

env_db = environ.get('FINANCE_DB')
DATABASE = r"C:\work\finance.db" if env_db is None else env_db
if not isfile(DATABASE):
    DATABASE = None  # FakeDao will be used

app = Flask(__name__)
# load all uppercase variables ad configuration
app.config.from_object(__name__)
app.debug = (node() != "anchor")  # anchor is the production box's hostname
app.config["APPLICATION_ROOT"] = URL_ROOT

# Load a dummy app at the root URL to give 404 errors.
# Serve app at APPLICATION_ROOT for localhost development.
application = DispatcherMiddleware(Flask('dummy_app'), {URL_ROOT: app})

import views
