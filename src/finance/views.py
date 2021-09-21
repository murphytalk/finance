"""
Routes and views for the flask application.
"""

from datetime import date, datetime
from flask import render_template, g, current_app, Response
from finance import finance_page, app
from finance.common.dao import Dao
from finance.common.report import StockAndEtfReport
import finance.common.dao.models as models
import logging.config
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def get_head_title():
    return "Finance" if current_app.config["DATABASE"] else "Finance Demo"


@finance_page.before_request
def before_request():
    g.dao = Dao(current_app.config["DATABASE"])
    g.dao.connect()
    logger.debug("dao opened %s", g.dao)


@finance_page.teardown_request
def teardown_request(exception):
    dao = getattr(g, "dao", None)
    logger.debug("closing dao %s", dao)
    if dao is not None:
        dao.close()


@dataclass
class RebalancingPlan:
    id: str
    name: str


@finance_page.route("/")
def summary():
    """Renders the home page."""
    return render_template(
        "index.jinja2",
        head_title=get_head_title(),
        title="Home Page",
        year=datetime.now().year,
        rebalancing_plans=[
            RebalancingPlan("plan1", "Step 1"),
            RebalancingPlan("plan2", "Step 2"),
            RebalancingPlan("merged_plan", "Merged Plan"),
        ],
    )


@finance_page.route("/stock.json")
def stock_json():
    r = StockAndEtfReport(g.dao, date.today())
    return Response(r.to_json(r.stock_positions()), mimetype="application/json")


@finance_page.route("/stock")
def stock():
    """Renders the contact page."""
    return render_template(
        "stock.jinja2",
        head_title=get_head_title(),
        title="Stock & ETF",
        year=datetime.now().year
    )


@finance_page.route("/fund")
def fund():
    """Renders the about page."""
    return render_template(
        "fund.jinja2",
        head_title=get_head_title(),
        title="Mutual Funds",
        year=datetime.now().year
    )


@finance_page.route("/db")
def db():
    return render_template(
        "db.jinja2",
        head_title=get_head_title(),
        title="Data Viewer",
        year=datetime.now().year,
    )


@finance_page.route("/asset.allocation/<instrument>")
def asset_allocation_json(instrument):
    return Response(asset_allocation(g.dao, instrument), mimetype="application/json")

@finance_page.route("/country.allocation/<instrument>")
def country_allocation_json(instrument):
    return Response(country_allocation(g.dao, instrument), mimetype="application/json")


@finance_page.route("/region.allocation/<instrument>")
def region_allocation_json(instrument):
    return Response(region_allocation(g.dao, instrument), mimetype="application/json")


@app.teardown_request
def remove_session(ex=None):
    models.finance_db_session.remove()
