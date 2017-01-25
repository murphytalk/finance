from datetime import date
from finance.api import api, fund_performance
from flask_restplus import Resource
from finance.common.report import FundReport2
from finance.api.endpoints import run_func_against_dao

ns = api.namespace('report', description='Various finance reports')


@ns.route('/fund')
class ReportFundPerformance(Resource):
    @api.marshal_list_with(fund_performance)
    def get(self):
        """
        Returns list of fund performance.
        """
        return run_func_against_dao(lambda dao: FundReport2(dao, date.today()).positions)
