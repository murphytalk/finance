"""
The flask application package.
"""
from os import environ
from os.path import isfile
from platform import node
from flask import Flask

env_db = environ.get('FINANCE_DB')
DATABASE = r"C:\Users\murph\Documents\work\finance.db" if env_db is None else env_db

if not isfile(DATABASE):
    DATABASE = None  #FakeDao will be used

app = Flask(__name__)
#load all uppercase variables ad confiuration
app.config.from_object(__name__)
app.debug = (node != "anchor") #anchor is the production box's hostname
import finance.views
