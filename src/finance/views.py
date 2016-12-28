"""
Routes and views for the flask application.
"""

from datetime import datetime, date
from flask import render_template, g, current_app, Response, url_for
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
    current_app.logger.debug('idx=%s', url_for("summary"))
    return render_template(
        'index.jinja2',
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
        'stock.jinja2',
        title='Stock & ETF',
        year=datetime.now().year,
        instrument_id_idx=14,
        url_idx=15
    )


@app.route('/fund')
def fund():
    """Renders the about page."""
    return render_template(
        'fund.jinja2',
        title='Mutual Funds',
        year=datetime.now().year,
        instrument_id_idx=9,
        url_idx=10
    )


@app.route('/fund.json')
def fund_json():
    r = FundReport(g.dao, date.today())
    return Response(r.to_json_packed(r.positions), mimetype='application/json')


@app.route('/asset.allocation/<instrument>')
def asset_allocation_json(instrument):
    return Response(asset_allocation(g.dao, instrument), mimetype='application/json')


@app.route('/region.allocation/<instrument>')
def region_allocation_json(instrument):
    return Response(region_allocation(g.dao, instrument), mimetype='application/json')


@app.route('/sum.json')
def sum_json():
    r = SummaryReport(g.dao, date.today())
    return Response(r.to_json_packed(r.report(g.dao)), mimetype='application/json')


@app.route('/db')
def db():
    return render_template(
        'db.jinja2',
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
