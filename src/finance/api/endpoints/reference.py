from finance.api import api
from finance.api import instrument_asset_allocation, asset_type, \
    instrument_region_allocation, region, broker, Instrument, instrument_type
from flask_restplus import Resource
from finance.api.endpoints import run_func_against_dao

ns = api.namespace('reference', description='Finance reference data')


@ns.route('/asset')
class ReferenceAsset(Resource):
    @api.marshal_list_with(asset_type)
    def get(self):
        """
        Return list of asset types
        """
        return run_func_against_dao(lambda dao: [{'id': x[0], 'type': x[1]} for x in dao.get_asset_types()])


@ns.route('/region')
class ReferenceRegion(Resource):
    @api.marshal_list_with(region)
    def get(self):
        """
        Return list of regions
        """
        return run_func_against_dao(lambda dao: [{'id': x[0], 'region': x[1]} for x in dao.get_regions()])


@ns.route('/broker')
class ReferenceBroker(Resource):
    @api.marshal_list_with(broker)
    def get(self):
        """
        Return list of brokers
        """
        return run_func_against_dao(lambda dao: [{'id': x[0], 'name': x[1],
                                                  'full_name': x[2]} for x in dao.get_brokers()])


@ns.route('/instrument/type')
class ReferenceAsset(Resource):
    @api.marshal_list_with(instrument_type)
    def get(self):
        """
        Return list of instrument types
        """
        return run_func_against_dao(lambda dao: [{'id': x[0], 'type': x[1]} for x in dao.get_instrument_types()])


def _get_instruments(dao, instrument_name=None):
    return [{'id': x['id'],
             'type': x['type'],
             'name': x['name'],
             'currency': x['currency'],
             'broker': x['broker'],
             'url': x['url'],
             'expense': x['expense']} for x in dao.get_instruments(instrument_name)];


@ns.route('/instrument')
class ReferenceInstruments(Resource):
    @api.marshal_list_with(Instrument)
    def get(self):
        """
        Return list of detail information of instruments
        """
        return run_func_against_dao(lambda dao: _get_instruments(dao))


@ns.route('/instrument/<string:instrument>')
@api.doc(params={'instrument': 'Instrument name'})
class ReferenceInstruments(Resource):
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
        return run_func_against_dao(lambda dao: dao.update_instrument(instrument, api.payload))


@ns.route('/instrument/allocation/asset/<string:instrument>')
@api.doc(params={'instrument': 'Instrument name'})
class ReferenceInstrumentAssetAllocation(Resource):
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


@ns.route('/instrument/allocation/region/<string:instrument>')
@api.doc(params={'instrument': 'Instrument name'})
class ReferenceInstrumentRegionAllocation(Resource):
    @api.marshal_list_with(instrument_region_allocation)
    def get(self, instrument):
        """
        Returns list of region allocations of instruments.
        :param instrument: instrument name
        """
        return run_func_against_dao(lambda dao: [
            {'regions': [{'region': x[0], 'ratio': x[1]} for x in dao.get_region_allocation(instrument_name=instrument)]}])

    @api.response(201, 'Instrument region allocations successfully updated.')
    @api.response(500, 'Cannot update instrument region allocations.')
    @api.expect(instrument_region_allocation)
    def post(self, instrument):
        """
        Create/Update region allocations for the given instrument.
        :param instrument: instrument name
        """
        return None, run_func_against_dao(
            lambda dao: 201 if dao.update_instrument_region_allocations(instrument, api.payload) else 500)
