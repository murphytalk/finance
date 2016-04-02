"""
The flask application package.
"""
from os import environ
from os.path import isfile
from platform import node
from flask import Flask
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.exceptions import NotFound

DEBUG = (node() != "anchor")  # anchor is the production box's hostname
URL_ROOT = "/finance"

env_db = environ.get('FINANCE_DB')
DATABASE = r"C:\work\finance.db" if env_db is None else env_db
if not isfile(DATABASE):
    DATABASE = None  # FakeDao will be used

app = Flask(__name__)
# load all uppercase variables ad configuration
app.config.from_object(__name__)
app.debug = DEBUG
app.config["APPLICATION_ROOT"] = URL_ROOT

application = DispatcherMiddleware(NotFound, {URL_ROOT: app})

import views
