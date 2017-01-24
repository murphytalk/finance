from datetime import  date
from finance.api import api, fund_performance
from flask_restplus import Resource
from flask import current_app
from finance.common.report import Dao, FundReport2

ns = api.namespace('report', description='Various finance reports')


@ns.route('/fund')
class ReportFundPerformance(Resource):
    @api.marshal_list_with(fund_performance)
    def get(self):
        """
        Returns list of fund performance.
        """
        dao = Dao(current_app.config['DATABASE'])
        dao.connect()
        r = FundReport2(dao, date.today())
        dao.close()
        return r.positions
