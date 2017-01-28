from finance.api import api, stock_transaction
from flask_restplus import Resource
from finance.api.endpoints import run_func_against_dao

ns = api.namespace('transaction', description='Financial transactions')


def _get_stock_transaction(dao, stock_name=None):
    return [{'Date': x['date'],
             'Symbol': x['symbol'],
             'Type': x['type'],
             'Price': x['price'],
             'Shares': x['shares'],
             'Fee': x['fee']} for x in dao.get_stock_transaction(stock_name)]


@ns.route('/stock')
class StockAll(Resource):
    @api.marshal_list_with(stock_transaction)
    def get(self):
        """
        Return list of stock/ETF transactions
        """
        return run_func_against_dao(lambda dao: _get_stock_transaction(dao))


@ns.route('/stock/<string:stock>')
@api.doc(params={'stock': 'Stock name'})
class Stock(Resource):
    @api.marshal_list_with(stock_transaction)
    def get(self, stock):
        """
        Return all transactions of the given stock/ETF
        """
        return run_func_against_dao(lambda dao: _get_stock_transaction(dao, stock))

    @api.response(201, 'Transaction successfully updated.')
    @api.response(500, 'Cannot update transaction.')
    @api.expect(stock_transaction)
    def post(self, stock):
        """
        Create/Update a stock/ETF transaction.
        :param stock: instrument name
        """
        return run_func_against_dao(lambda dao: 201 if dao.update_stock_transaction(stock, api.payload) else 500)

