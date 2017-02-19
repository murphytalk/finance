import logging
from flask_restplus import fields
from flask_restplus import Api

log = logging.getLogger(__name__)

api = Api(version='1.0', title='My Finance API',
          description='Query and manipulate my finance portal data')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)
    return {'message': message}, 500

fund_performance = api.model('Fund performance', {
    'broker': fields.String(description='Broker name'),
    'name': fields.String(description='Instrument name'),
    'expense_ratio': fields.Float(description='Expense ratio'),
    'price': fields.Float(description='Last price'),
    'amount': fields.Float(description='Amount'),
    'capital': fields.Float(description='Capital'),
    'value': fields.Float(description='Market value'),
    'profit': fields.Float(description='Profit'),
    'date': fields.String(description='Date'),
    'instrument_id': fields.Integer(description='Instrument ID'),
    'url': fields.String(description='Instrument details')
})

asset_allocation = api.model('Asset allocation', {
    'asset': fields.String(description='Asset type', required=True),
    'ratio': fields.Float(description='Allocation percentage', required=True)
})

instrument_asset_allocation = api.model('Instrument asset allocation', {
    'assets': fields.List(fields.Nested(asset_allocation), description='Asset allocations', required=True)
})

asset_type = api.model('Asset types', {
    'id':   fields.Integer(description='Asset ID'),
    'type': fields.String(description='Asset type')
})

country = api.model('Country', {
    'id':   fields.Integer(description='Country ID'),
    'country': fields.String(description='Country')
})

instrument_type = api.model('Instrument types', {
    'id':   fields.Integer(description='Instrument type ID'),
    'type': fields.String(description='Instrument type')
})

broker = api.model('Broker', {
    'id':   fields.Integer(description='Broker ID'),
    'name': fields.String(description='Country'),
    'full_name': fields.String(description='Country')
})

country_allocation = api.model('Country allocation', {
    'country': fields.String(description='Country', required=True),
    'ratio': fields.Float(description='Allocation percentage', required=True)
})

instrument_country_allocation = api.model('Instrument country allocation', {
    'countries': fields.List(fields.Nested(country_allocation), description='Country allocations', required=True)
})

Instrument = api.model('Instrument', {
    'id':   fields.Integer(description='Instrument ID', required=False),
    'name': fields.String(description='Instrument name', required=True),
    'type': fields.String(description='Instrument type', required=False),
    'broker': fields.String(description='Broker', required=False),
    'currency': fields.String(description='Currency', required=False),
    'url': fields.String(description='Instrument URL', required=False),
    'expense': fields.Float(description='Expense ratio', required=False),
})

stock_transaction = api.model('Stock transactions', {
    'Date':  fields.String(description='Transaction date'),
    'Symbol': fields.String(description='Stock/ETF symbol'),
    'Type':  fields.String(description='Transaction type'),
    'Price':  fields.Float(description='Price'),
    'Shares': fields.Float(description='Shares'),
    'Fee':  fields.Float(description='Fee'),
})

stock_quote = api.model('Stock quote', {
    'Date':  fields.String(description='Closing date'),
    'Symbol': fields.String(description='Stock/ETF symbol'),
    'Price':  fields.Float(description='Price'),
})

stock_quotes = api.model('Stock quotes', {
    'quotes': fields.List(fields.Nested(stock_quote), description='Multiple days quotes of the given instrument')
})

xccy_quote = api.model('Xccy quotes', {
    'Date':  fields.String(description='Closing date'),
    'From': fields.String(description='Exchange from currency'),
    'To': fields.String(description='Exchange to currency'),
    'Rate':  fields.Float(description='Exchange rate'),
})

_simple_instrument = api.model('Simple Instrument', {
    'id':   fields.Integer(description='Instrument ID', required=False),
    'name': fields.String(description='Instrument name', required=True),
})

instrument_filter = api.model('Instrument filter', {
    'name': fields.String(description='Filter name'),
    'instruments': fields.List(fields.Nested(_simple_instrument), description='Instruments'),
})


