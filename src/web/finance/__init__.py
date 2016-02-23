"""
The flask application package.
"""
import os
from flask import Flask

env_db = os.environ.get('FINANCE_DB')
DATABASE = r"C:\Users\murph\Documents\work\finance.db" if env_db is None else env_db

app = Flask(__name__)
#load all uppercase variables ad confiuration
app.config.from_object(__name__)
print app.config['DATABASE'] 
import finance.views
