"""
Routes and views for the flask application.
"""

from datetime import datetime, date
from flask import render_template, g, current_app, Response
from finance import app

# add ../../common to path
import os, sys, inspect
from os.path import sep

common_folder = os.path.realpath(os.path.abspath(
    os.path.split(inspect.getfile(inspect.currentframe()))[0])) + sep + '..' + sep + '..' + sep + 'common'
if common_folder not in sys.path:
    sys.path.insert(0, common_folder)

# from utils import get_utc_offset,get_current_date_epoch,epoch2datetime
from dao import factory
from report import Report, raw_quote, raw_xccy, raw_trans


@app.before_request
def before_request():
    g.dao = factory(current_app.config['DATABASE'])
    current_app.logger.debug('dao opened %s', g.dao)


@app.teardown_request
def teardown_request(exception):
    dao = getattr(g, 'dao', None)
    current_app.logger.debug('closing dao %s', dao)
    if dao is not None:
        dao.close()


@app.route('/')
def summary():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )


@app.route('/stock.json')
def stock_json():
    r = Report(g.dao, date.today())
    return Response(r.to_json(r.list()), mimetype='application/json')


@app.route('/stock')
def stock():
    """Renders the contact page."""
    return render_template(
        'stock.html',
        title='Stock & ETF',
        year=datetime.now().year
    )


@app.route('/fund')
def fund():
    """Renders the about page."""
    return render_template(
        'fund.html',
        title='Mutual Funds',
        year=datetime.now().year
    )


@app.route('/db')
def db():
    return render_template(
        'db.html',
        title='Data Viewer',
        year=datetime.now().year
    )


@app.route('/db/quote.json')
def db_quote_json():
    return Response(raw_quote(g.dao), mimetype='application/json')


@app.route('/db/xccy.json')
def db_xccy_json():
    return Response(raw_xccy(g.dao), mimetype='application/json')


@app.route('/db/trans.json')
def db_trans_json():
    return Response(raw_trans(g.dao), mimetype='application/json')
