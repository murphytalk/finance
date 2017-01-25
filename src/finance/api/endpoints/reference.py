from finance.api import api
from finance.api import instrument_asset_allocation, asset_type, instrument_region_allocation, region
from flask_restplus import Resource
from finance.api.endpoints import run_func_against_dao

ns = api.namespace('reference', description='Finance reference data')


@ns.route('/asset_type')
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
        Return list of  regions
        """
        return run_func_against_dao(lambda dao: [{'id': x[0], 'region': x[1]} for x in dao.get_regions()])


@ns.route('/instrument/asset_allocation/<string:instrument>')
class ReferenceInstrumentAssetAllocation(Resource):
    @api.marshal_list_with(instrument_asset_allocation)
    # the following method expects the parameter in the query instead of URL
    # @ns.param('instrument', 'The instrument name')
    def get(self, instrument):
        """
        Returns list of asset allocations of instruments.
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


@ns.route('/instrument/region_allocation/<string:instrument>')
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
