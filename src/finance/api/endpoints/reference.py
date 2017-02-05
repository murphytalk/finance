from finance.api import api
from finance.api import asset_type, country, broker, instrument_type
from flask_restplus import Resource
from finance.api.endpoints import run_func_against_dao

import logging.config
logger = logging.getLogger(__name__)

ns = api.namespace('reference', description='Financial reference data')


@ns.route('/asset')
class Asset(Resource):
    @api.marshal_list_with(asset_type)
    def get(self):
        """
        Return list of asset types
        """
        return run_func_against_dao(lambda dao: [{'id': x[0], 'type': x[1]} for x in dao.get_asset_types()])


@ns.route('/country')
class Country(Resource):
    @api.marshal_list_with(country)
    def get(self):
        """
        Return list of countries
        """
        return run_func_against_dao(lambda dao: [{'id': x[0], 'country': x[1]} for x in dao.get_countrys()])


@ns.route('/broker')
class Broker(Resource):
    @api.marshal_list_with(broker)
    def get(self):
        """
        Return list of brokers
        """
        return run_func_against_dao(lambda dao: [{'id': x[0], 'name': x[1],
                                                  'full_name': x[2]} for x in dao.get_brokers()])


@ns.route('/instrument/type')
class InstrumentType(Resource):
    @api.marshal_list_with(instrument_type)
    def get(self):
        """
        Return list of instrument types
        """
        return run_func_against_dao(lambda dao: [{'id': x[0], 'type': x[1]} for x in dao.get_instrument_types()])



