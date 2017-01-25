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
    'name': fields.String(description='Region'),
    'full_name': fields.String(description='Region')
})

region_allocation = api.model('Region allocation', {
    'region': fields.String(description='Region', required=True),
    'ratio': fields.Float(description='Allocation percentage', required=True)
})

instrument_region_allocation = api.model('Instrument region allocation', {
    'regions': fields.List(fields.Nested(region_allocation), description='Region allocations', required=True)
})

Instrument = api.model('Instrument', {
    'id':   fields.Integer(description='Instrument ID', required=False),
    'name': fields.String(description='Instrument name', required=False),
    'type': fields.String(description='Instrument type'),
    'broker': fields.String(description='Broker'),
    'currency': fields.String(description='Currency'),
    'url': fields.String(description='Instrument URL'),
    'expense': fields.Float(description='Expense ratio'),
})

