from finance.api import api, stock_transaction, stock_quote, stock_quotes, xccy_quote, xccy_quotes, funds_performance
from flask_restx import Resource
from finance.api.endpoints import run_func_against_dao
from flask import request

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


def _get_stock_quote(dao, stock_name=None, max_days=None):
    return [{'Date': x['date'],
             'Symbol': x['symbol'],
             'Price': x['price']} for x in dao.get_stock_quote(stock_name, max_days)]


def _get_int_from_query_param(name):
    value = request.args.get(name)  # is there better way to capture parameter from query?
    if value:
        try:
            value = int(value)
        except ValueError:
            value = None
    return value


@ns.route('/stock/quote')
class StockQuoteAll(Resource):
    @api.marshal_list_with(stock_quote)
    @ns.param('max_days', 'Only return quotes from today to max_days days earlier if specified')
    def get(self):
        """
        Return list of stock/ETF quotes
        """
        return run_func_against_dao(lambda dao: _get_stock_quote(dao, None, _get_int_from_query_param('max_days')))


@ns.route('/stock/quote/<string:stock>')
@api.doc(params={'stock': 'Stock name'})
class StockQuote(Resource):
    @api.marshal_list_with(stock_quote)
    @ns.param('max_days', 'Only return quotes from today to max_days days earlier if specified')
    def get(self, stock):
        """
        Return all quotes of the given stock/ETF
        """
        return run_func_against_dao(lambda dao: _get_stock_quote(dao, stock, _get_int_from_query_param('max_days')))

    @api.response(201, 'Quote successfully updated.')
    @api.response(500, 'Cannot update quote.')
    @api.expect(stock_quotes)
    def post(self, stock):
        return run_func_against_dao(lambda dao: 201 if dao.update_stock_quotes(stock, api.payload) else 500)


@ns.route('/fund/performance/<string:fund>')
@api.doc(params={'fund': 'Fund name'})
class FundPerformance(Resource):
    @api.response(201, 'Fund performance successfully updated.')
    @api.response(500, 'Cannot update fund performance.')
    @api.expect(funds_performance)
    def post(self, fund):
        return run_func_against_dao(lambda dao: 201 if dao.update_fund_performance(fund, api.payload) else 500)


def _get_xccy_quote(dao, ccy_pair=None, max_days=None):
    return [{'Date': x['Date'],
             'From': x['From'],
             'To': x['To'],
             'Rate': x['Rate']} for x in dao.get_xccy_quote(ccy_pair, max_days)]


@ns.route('/xccy')
class XccyQuoteAll(Resource):
    @api.marshal_list_with(xccy_quote)
    @ns.param('max_days', 'Only return quotes of last max_days days earlier if specified')
    def get(self):
        """
        Return list of the quotes of the all (known) currency pairs
        """
        return run_func_against_dao(lambda dao: _get_xccy_quote(dao, None, _get_int_from_query_param('max_days')))

    @api.response(201, 'Quote successfully updated.')
    @api.response(500, 'Cannot update quote.')
    @api.expect(xccy_quotes)
    def post(self):
        return run_func_against_dao(lambda dao: 201 if dao.update_xccy_quotes(api.payload) else 500)


@ns.route('/xccy/<string:from_ccy>/<string:to_ccy>')
@api.doc(params={'from_ccy': 'The currency to exchange from', 'to_ccy': 'The currency to exchange to'})
class XccyQuote(Resource):
    @api.marshal_list_with(xccy_quote)
    @ns.param('max_days', 'Only return quotes from today to max_days days earlier if specified')
    def get(self, from_ccy, to_ccy):
        """
        Return all quotes of the given currency pair
        """
        return run_func_against_dao(lambda dao: _get_xccy_quote(dao, (from_ccy, to_ccy),
                                                                _get_int_from_query_param('max_days')))
