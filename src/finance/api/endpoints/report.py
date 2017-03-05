from datetime import date
from finance.api import api, fund_performance, positions
from flask_restplus import Resource
from finance.common.report import FundReport, StockReport2
from finance.api.endpoints import run_func_against_dao

ns = api.namespace('report', description='Financial reports')


@ns.route('/fund')
class FundPerformance(Resource):
    @api.marshal_list_with(fund_performance)
    def get(self):
        """
        Returns list of fund performance.
        """
        return run_func_against_dao(lambda dao: FundReport(dao, date.today()).positions)


@ns.route('/positions')
class Positions(Resource):
    @api.marshal_with(positions)
    def get(self):
        """
        Return a summary of all positions
        """
        def _get_position(dao, report):
            return [{'instrument': {'id': p['instrument'], 'name':p['symbol']},
                     'asset_allocation':
                         [{'asset': x[0],
                           'ratio': x[1]
                           } for x in dao.get_asset_allocation(instrument_id=p['instrument'])],
                     'country_allocation':
                         [{'country': x[0],
                           'ratio': x[1]
                           } for x in dao.get_country_allocation(instrument_id=p['instrument'])],
                     'region_allocation':
                         [{'region': x[0],
                           'ratio': x[1]
                           } for x in dao.get_region_allocation(instrument_id=p['instrument'])],
                     'ccy': p['ccy'],
                     'xccy': p['xccy'],
                     'shares': p['shares'],
                     'price': p['price'],
                     'capital': -p['liquidated']} for p in report if p['shares'] > 0]

        def _get_stock_etf_positions(dao):
            r = StockReport2(dao, date.today()).stock_positions()
            return _get_position(dao, r['ETF']), _get_position(dao, r['Stock'])

        def _get_all(dao):
            stocks = _get_stock_etf_positions(dao)
            # change to the same format as stock position
            # Japan mutual funds have different ways to calculate amount(口),
            # we simplify here by assigning total market value (scraped from broker's page) to price and keep share be 1
            funds = [{'instrument': p['instrument_id'],
                      'symbol': p['name'],
                      'ccy': 'JPY',
                      'xccy': 1,
                      'shares': 1,
                      'price': p['value'],
                      'liquidated': -p['capital']
                      } for p in FundReport(dao, date.today()).positions]
            return {'ETF': stocks[0],
                    'Stock': stocks[1],
                    'Funds': _get_position(dao, funds),
                    'Cash': [{'ccy': x[0], 'broker': x[1], 'balance': x[2], 'xccy': x[3]}
                             for x in dao.get_cash_balance()]}

        return run_func_against_dao(lambda dao: _get_all(dao))
