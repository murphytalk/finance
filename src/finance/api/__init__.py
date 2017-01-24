import logging
from flask_restplus import fields
from flask_restplus import Api
#from finance import DEBUG

log = logging.getLogger(__name__)

api = Api(version='1.0', title='My Finance API',
          description='Manipulate my finance portal data')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if True:#DEBUG:
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
