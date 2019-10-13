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

region = api.model('Region', {
    'id':   fields.Integer(description='Region ID'),
    'region': fields.String(description='Region')
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

region_allocation = api.model('Region allocation', {
    'region': fields.String(description='Region', required=True),
    'ratio': fields.Float(description='Allocation percentage', required=True)
})

instrument_country_allocation = api.model('Instrument country allocation', {
    'countries': fields.List(fields.Nested(country_allocation), description='Country allocations', required=True)
})

instrument_region_allocation = api.model('Instrument region allocation', {
    'regions': fields.List(fields.Nested(region_allocation), description='Region allocations', required=True)
})

Instrument = api.model('Instrument', {
    'id':   fields.Integer(description='Instrument ID', required=False),
    'name': fields.String(description='Instrument name', required=True),
    'type': fields.String(description='Instrument type', required=False),
    'broker': fields.String(description='Broker', required=False),
    'currency': fields.String(description='Currency', required=False),
    'url': fields.String(description='Instrument URL', required=False),
    'expense': fields.Float(description='Expense ratio', required=False),
    'active':   fields.Integer(description='Active', required=False),
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

funds_performance = api.model('Funds performance', {
    'date':  fields.String(description='Closing date'),
    'name': fields.String(description='Funds name'),
    'amount':  fields.Integer(description='Amount'),
    'price':  fields.Float(description='Price'),
    'value':  fields.Float(description='Market value'),
    'capital':  fields.Float(description='Capital'),
    'profit':  fields.Float(description='Profit')
})

xccy_quote = api.model('Xccy quote', {
    'Date':  fields.String(description='Closing date'),
    'From': fields.String(description='Exchange from currency'),
    'To': fields.String(description='Exchange to currency'),
    'Rate':  fields.Float(description='Exchange rate'),
})

xccy_quotes = api.model('Xccy quotes', {
    'quotes': fields.List(fields.Nested(xccy_quote), description='Multiple days quotes of the given xccy')
})

_simple_instrument = api.model('Simple Instrument', {
    'id':   fields.Integer(description='Instrument ID', required=False),
    'name': fields.String(description='Instrument name', required=True),
})

instrument_filter = api.model('Instrument filter', {
    'name':  fields.String(description='Filter name'),
    'extra': fields.String(description='Extra filter'),
    'instruments': fields.List(fields.Nested(_simple_instrument), description='Instruments'),
})

instrument_position = api.model('Position of one instrument', {
    'instrument': fields.Nested(_simple_instrument, description='Instrument'),
    # 'broker': fields.String(description='The broker that keeps the position'),
    'asset_allocation': fields.List(fields.Nested(asset_allocation), description='Asset allocations'),
    'country_allocation': fields.List(fields.Nested(country_allocation), description='Country allocations'),
    'region_allocation': fields.List(fields.Nested(region_allocation), description='Region allocations'),
    'ccy': fields.String(description='Currency'),
    'xccy': fields.Float(description='Currency exchange rate to JPY'),
    'shares': fields.Float(description='Shares'),
    'price': fields.Float(description='Current market price'),
    'capital': fields.Float(description='Invested capital')
})

cash = api.model('Cash balance', {
    'ccy': fields.String(description='Currency', readonly=True),
    'broker': fields.String(description='The broker that we keeps the position with', readonly=True),
    'balance': fields.Float(description='Cash balance'),
    'xccy': fields.Float(description='To JPY exchange rate', readonly=True)
})

positions = api.model('Summary of all positions', {
    'ETF': fields.List(fields.Nested(instrument_position), description='ETF positions'),
    'Stock': fields.List(fields.Nested(instrument_position), description='Stock positions'),
    'Funds': fields.List(fields.Nested(instrument_position), description='Mutual funds positions'),
    'Cash': fields.List(fields.Nested(cash), description='Cash balance')
})

portfolio_alloc = api.model('PortfolioAllocation', {
    'instrument': fields.String(description='Instrument name'),
    'shares': fields.Integer(description='Shares'),
    'price': fields.Float(description='Closing price'),
    'target_allocation': fields.Float(description='Taget allocation in percentage'),
    'market_value': fields.Integer(description='Current market value'),
    'current_allocation': fields.Float(description='Current allocation in percentage')
})

portfolio = api.model('Portfolio', {
    'name': fields.String(description='Portfolio name', required=True),
    'allocations': fields.List(fields.Nested(portfolio_alloc), description='Portfolio allocations'),
})
