"""
Routes and views for the flask application.
"""

from datetime import datetime, date
from flask import render_template, g, current_app, Response, url_for
from finance import app, finance_page
from finance.common.report import *


def get_head_title():
    return 'Finance' if current_app.config['DATABASE'] else 'Finance Demo'


@finance_page.before_request
def before_request():
    g.dao = Dao(current_app.config['DATABASE'])
    g.dao.connect()
    current_app.logger.debug('dao opened %s', g.dao)


@finance_page.teardown_request
def teardown_request(exception):
    dao = getattr(g, 'dao', None)
    current_app.logger.debug('closing dao %s', dao)
    if dao is not None:
        dao.close()


@finance_page.route('/')
def summary():
    """Renders the home page."""
    current_app.logger.debug('idx=%s', url_for("finance_page.summary"))
    return render_template(
        'index.jinja2',
        head_title=get_head_title(),
        title='Home Page',
        year=datetime.now().year,
    )


@finance_page.route('/stock.json')
def stock_json():
    r = StockReport(g.dao, date.today())
    return Response(r.to_json(r.stock_positions()), mimetype='application/json')


@finance_page.route('/stock')
def stock():
    """Renders the contact page."""
    return render_template(
        'stock.jinja2',
        head_title=get_head_title(),
        title='Stock & ETF',
        year=datetime.now().year,
        instrument_id_idx=14,
        url_idx=15
    )


@finance_page.route('/fund')
def fund():
    """Renders the about page."""
    return render_template(
        'fund.jinja2',
        head_title=get_head_title(),
        title='Mutual Funds',
        year=datetime.now().year,
        instrument_id_idx=9,
        url_idx=10
    )


@finance_page.route('/fund.json')
def fund_json():
    r = FundReport(g.dao, date.today())
    return Response(r.to_json_packed(r.positions), mimetype='application/json')


@finance_page.route('/asset.allocation/<instrument>')
def asset_allocation_json(instrument):
    return Response(asset_allocation(g.dao, instrument), mimetype='application/json')


@finance_page.route('/region.allocation/<instrument>')
def region_allocation_json(instrument):
    return Response(region_allocation(g.dao, instrument), mimetype='application/json')


@finance_page.route('/sum.json')
def sum_json():
    r = SummaryReport(g.dao, date.today())
    return Response(r.to_json_packed(r.report(g.dao)), mimetype='application/json')


@finance_page.route('/db')
def db():
    return render_template(
        'db.jinja2',
        head_title=get_head_title(),
        title='Data Viewer',
        year=datetime.now().year
    )


@finance_page.route('/db/quote.json')
def db_quote_json():
    return Response(raw_quote(g.dao), mimetype='application/json')


@finance_page.route('/db/xccy.json')
def db_xccy_json():
    return Response(raw_xccy(g.dao), mimetype='application/json')


@finance_page.route('/db/trans.json')
def db_trans_json():
    return Response(raw_trans(g.dao), mimetype='application/json')
