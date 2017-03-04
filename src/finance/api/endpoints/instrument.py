from finance.api import api
from finance.api import instrument_asset_allocation, instrument_country_allocation, instrument_region_allocation
from finance.api import Instrument, instrument_filter
from flask_restplus import Resource
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


@ns.route('/filter')
class InstrumentFilters(Resource):
    @api.marshal_list_with(instrument_filter)
    def get(self):
        """
        Return list of instrument filters
        """
        def _gen(filters):
            return [{'name': x, 'extra': filters[x]['extra'], 'instruments': filters[x]['instruments']} for x in filters.keys()]
        return run_func_against_dao(lambda dao: _gen(dao.get_filters()))


@ns.route('/filter/<string:name>')
@api.doc(params={'name': 'Filter name'})
class InstrumentFilter(Resource):
    @api.marshal_with(instrument_filter)
    def get(self, name):
        """
        Returns the instruments in the given filter
        :param name: filter name
        """
        def _gen(dao):
            for n, f in dao.get_filters(name).items():
                return {'name': n, 'instruments': f['instruments'], 'extra': f['extra']}

        return run_func_against_dao(lambda dao: _gen(dao))

    @api.response(201, 'Instrument filter successfully updated.')
    @api.response(500, 'Cannot update instrument filter.')
    @api.expect(instrument_filter)
    def post(self, name):
        """
        Create/Update given instrument filter.
        :param name filter name
        """
        return None, run_func_against_dao(
            lambda dao: 201 if dao.update_filter(name, api.payload) else 500)

