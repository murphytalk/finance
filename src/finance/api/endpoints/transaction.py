from finance.api import api, stock_transaction
from flask_restplus import Resource
from finance.api.endpoints import run_func_against_dao

ns = api.namespace('transaction', description='Financial transactions')


@ns.route('/stock/transaction')
class StockTransactions(Resource):
    @api.marshal_list_with(stock_transaction)
    def get(self):
        """
        Return list of stock/ETF transactions
        """
        return run_func_against_dao(lambda dao: [{
                    'Date': x['date'],
                    'Symbol': x['symbol'],
                    'Type': x['type'],
                    'Price': x['price'],
                    'Shares': x['shares'],
                    'Fee': x['fee']} for x in dao.get_stock_transaction()]
 )