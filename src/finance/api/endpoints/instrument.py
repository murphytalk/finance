from finance.api import api
from finance.api import instrument_asset_allocation, instrument_country_allocation, instrument_region_allocation, cash
from finance.api import Instrument
from flask_restx import Resource
from finance.api.endpoints import run_func_against_dao

import logging.config
logger = logging.getLogger(__name__)

ns = api.namespace('instrument', description='Financial instruments')


def _get_instruments(dao, instrument_name=None):
    return [{'id': x['id'],
             'type': x['type'],
             'name': x['name'],
             'currency': x['currency'],
             'broker': x['broker'],
             'url': x['url'],
             'active': x['active'],
             'expense': x['expense']} for x in dao.get_instruments(instrument_name)]


@ns.route('/')
class Instruments(Resource):
    @api.marshal_list_with(Instrument)
    def get(self):
        """
        Return list of detail information of instruments
        """
        return run_func_against_dao(lambda dao: _get_instruments(dao))


@ns.route('/<string:instrument>')
@api.doc(params={'instrument': 'Instrument name'})
class Instrument(Resource):
    @api.marshal_list_with(Instrument)
    def get(self, instrument):
        """
        Return detail information of the given instrument
        """
        return run_func_against_dao(lambda dao: _get_instruments(dao, instrument))

    @api.response(201, 'Instrument successfully updated.')
    @api.response(500, 'Cannot update instrument.')
    @api.expect(Instrument)
    def post(self, instrument):
        """
        Create/Update detail information of the given instrument.
        :param instrument: instrument name
        """
        return run_func_against_dao(lambda dao: 201 if dao.update_instrument(instrument, api.payload) else 500)


@ns.route('/allocation/asset/<string:instrument>')
@api.doc(params={'instrument': 'Instrument name'})
class InstrumentAssetAllocation(Resource):
    @api.marshal_list_with(instrument_asset_allocation)
    # the following method expects the parameter in the query instead of URL
    # @ns.param('instrument', 'The instrument name')
    def get(self, instrument):
        """
        Returns list of asset allocations of the given instrument.
        :param instrument: instrument name
        """
        return run_func_against_dao(lambda dao: [
            {'assets': [{'asset': x[0], 'ratio': x[1]} for x in dao.get_asset_allocation(instrument_name=instrument)]}])

    @api.response(201, 'Instrument asset allocations successfully updated.')
    @api.response(500, 'Cannot update instrument asset allocations.')
    @api.expect(instrument_asset_allocation)
    def post(self, instrument):
        """
        Create/Update asset allocations for the given instrument.
        :param instrument: instrument name
        """
        return None, run_func_against_dao(
            lambda dao: 201 if dao.update_instrument_asset_allocations(instrument, api.payload) else 500)


@ns.route('/allocation/country/<string:instrument>')
@api.doc(params={'instrument': 'Instrument name'})
class InstrumentCountryAllocation(Resource):
    @api.marshal_list_with(instrument_country_allocation)
    def get(self, instrument):
        """
        Returns list of country allocations of instruments.
        :param instrument: instrument name
        """
        return run_func_against_dao(lambda dao: [
            {'countries': [{'country': x[0], 'ratio': x[1]} for x in dao.get_country_allocation(instrument_name=instrument)]}])

    @api.response(201, 'Instrument country allocations successfully updated.')
    @api.response(500, 'Cannot update instrument country allocations.')
    @api.expect(instrument_country_allocation)
    def post(self, instrument):
        """
        Create/Update country allocations for the given instrument.
        :param instrument: instrument name
        """
        return None, run_func_against_dao(
            lambda dao: 201 if dao.update_instrument_country_allocations(instrument, api.payload) else 500)


@ns.route('/allocation/region/<string:instrument>')
@api.doc(params={'instrument': 'Instrument name'})
class InstrumentRegionAllocation(Resource):
    @api.marshal_list_with(instrument_region_allocation)
    def get(self, instrument):
        """
        Returns list of region allocations of instruments.
        :param instrument: instrument name
        """
        return run_func_against_dao(lambda dao: [
            {'regions': [{'Region': x[0], 'ratio': x[1]} for x in dao.get_region_allocation(instrument_name=instrument)]}])


@ns.route('/cash')
class CashList(Resource):
    @api.marshal_list_with(cash)
    def get(self):
        return run_func_against_dao(lambda dao: [{'ccy': x[0], 'broker': x[1], 'balance': x[2], 'xccy': x[3]}
                                                 for x in dao.get_cash_balance()])


@ns.route('/cash/<string:ccy>/<string:broker>')
@api.doc(params={'ccy': 'Currency', 'broker': 'Broker'})
class Cash(Resource):
    @api.response(201, 'Cash balance successfully updated.')
    @api.response(500, 'Cannot update cash balance.')
    @api.expect(cash)
    def post(self, ccy, broker):
        return None, run_func_against_dao(
            lambda dao: 201 if dao.update_cash_balance(ccy, broker, api.payload) else 500)


@ns.route('/cash/adjust/<string:ccy>/<string:broker>')
@api.doc(params={'ccy': 'Currency', 'broker': 'Broker'})
class Cash(Resource):
    @api.response(201, 'Cash balance successfully updated.')
    @api.response(500, 'Cannot update cash balance.')
    @api.expect(cash)
    def post(self, ccy, broker):
        return None, run_func_against_dao(
            lambda dao: 201 if dao.update_cash_balance(ccy, broker, api.payload, True) else 500)

