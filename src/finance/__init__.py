"""
The flask application package.
"""
from platform import node

import flask_admin as admin
from flask import Flask, Blueprint, send_from_directory
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import DateTimeBetweenFilter
from wtforms.fields import DateTimeField, SelectField
import finance.common.dao.models as models
from finance.api import api
from finance.api.endpoints.instrument import ns as api_instrument
from finance.api.endpoints.reference import ns as api_reference
from finance.api.endpoints.report import ns as api_reports
from finance.api.endpoints.transaction import ns as api_transaction

import os
import os.path
from pathlib import Path

# check hostname to determine if it is a production deployment
deployed_in_production = node() == "anchor"

DEBUG = not deployed_in_production
DATABASE = models.DATABASE

# deployed behind ngix
URL_ROOT = ("/finance" if DATABASE is not None else "/finance_demo")
print("URL root at {}".format(URL_ROOT))
# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False
SWAGGER_UI_JSONEDITOR = True

app = Flask(__name__)
# load all uppercase variables as configuration
app.config.from_object(__name__)
app.debug = DEBUG

# flask admin needs a session
app.secret_key = "I don't call this secret"
app.config['SESSION_TYPE'] = 'filesystem'

# next generation, the SPA
p = Path(os.path.abspath(__file__))
static_dir = '{}/finance-ng/dist/finance-ng'.format(Path(os.path.abspath(__file__)).parent.parent.parent)
ng = Blueprint('ng', __name__, url_prefix='/ng')


@ng.route('/<path:filename>')
def ng_static(filename):
    req = filename
    if '.' not in filename:
        filename = 'index.html'
    print('{} => {}/{}'.format(req, static_dir, filename))
    return send_from_directory(static_dir,
                               filename, as_attachment=False)


@ng.route('/')
def ng_static_root():
    return ng_static('index.html')


app.register_blueprint(ng)

# legacy finance page
finance_page = Blueprint('finance_page', __name__, url_prefix=URL_ROOT)
# needed for the URLs, and finance_page needs to be defined before import
from finance import views 

# need to register after all URLS are defined in views
app.register_blueprint(finance_page)

api_page = Blueprint('api', __name__, url_prefix='%s/api' % URL_ROOT)
api.init_app(api_page)
api.add_namespace(api_reports)
api.add_namespace(api_reference)
api.add_namespace(api_instrument)
api.add_namespace(api_transaction)
app.register_blueprint(api_page)

# Create admin
admin = admin.Admin(app, name='Finance Admin', url='%s/admin' % URL_ROOT, template_mode='bootstrap3')


class ModelViewWithDate(ModelView):
    # My date field is a DateTimeField
    form_overrides = dict(date=DateTimeField)
    # To show the datetime picker widget
    form_widget_args = {
        'date': {
            "data-date-format": "YYYY-MM-DD HH:mm:ss",
            "data-role": "datetimepicker"
        }
    }
    column_sortable_list = ('date',)
    column_filters = ('instrument',)
    column_hide_backrefs = False
    column_display_all_relations = True


class InstrumentView(ModelView):
    column_filters = [
        'name', 'instrument_type',
        'currency',
        'expense'
    ]
    inline_models = (models.AssetAllocation, models.CountryAllocation)


class FundsPerformanceView(ModelViewWithDate):
    column_filters = [
        'instrument',
        DateTimeBetweenFilter(column=models.FundPerformance.date, name='Date'),
    ]


class StockTransactionView(ModelViewWithDate):
    column_filters = [
        'instrument',
        DateTimeBetweenFilter(column=models.StockTransaction.date, name='Date'),
    ]

    form_overrides = dict(
        type=SelectField,
        date=DateTimeField
    )

    form_args = dict(
        type=dict(
            choices=[
                ('BUY', 'BUY'),
                ('SELL', 'SELL'),
                ('SPLIT', 'SPLIT')
            ]
        )
    )


class QuoteView(ModelViewWithDate):
    column_filters = [
        'instrument',
        DateTimeBetweenFilter(column=models.Quote.date, name='Date'),
    ]


class FilterByRegionView(ModelView):
    column_filters = ['region']


class PortfolioView(ModelView):
    inline_models = (models.PortfolioAllocation,)


# Add views
for view, model in (
        (InstrumentView, models.Instrument),
        (StockTransactionView, models.StockTransaction),
        (FundsPerformanceView, models.FundPerformance),
        (QuoteView, models.Quote),
        (ModelView, models.Cash),
        (ModelView, models.Broker),
        (ModelView, models.Asset),
        (ModelView, models.Country),
        (ModelView, models.Currency),
        (ModelView, models.Region),
        (FilterByRegionView, models.CountryByRegion),
        (ModelView, models.InstrumentType),
        (PortfolioView, models.Portfolio),
):
    admin.add_view(view(model, models.finance_db_session))
