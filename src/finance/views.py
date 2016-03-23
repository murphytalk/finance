"""
Routes and views for the flask application.
"""

from datetime import datetime, date
from flask import render_template, g, current_app, Response
from finance import app
from common.dao import factory
from common.report import *


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
    r = StockReport(g.dao, date.today())
    return Response(r.to_json(r.stock_positions()), mimetype='application/json')


@app.route('/stock')
def stock():
    """Renders the contact page."""
    return render_template(
        'stock.html',
        title='Stock & ETF',
        year=datetime.now().year,
        instrument_id_idx=12,
        url_idx=13
    )


@app.route('/fund')
def fund():
    """Renders the about page."""
    return render_template(
        'fund.html',
        title='Mutual Funds',
        year=datetime.now().year,
        instrument_id_idx=9,
        url_idx=10
    )


@app.route('/fund.json')
def fund_json():
    r = FundReport(g.dao, date.today())
    return Response(r.to_json(r.positions), mimetype='application/json')


@app.route('/asset.allocation/<instrument>')
def asset_allocation_json(instrument):
    return Response(asset_allocation(g.dao, instrument), mimetype='application/json')


@app.route('/region.allocation/<instrument>')
def region_allocation_json(instrument):
    return Response(region_allocation(g.dao, instrument), mimetype='application/json')


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
