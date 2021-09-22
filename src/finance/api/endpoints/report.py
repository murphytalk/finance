from datetime import date
from finance.api import api, fund_performance, positions, portfolio, portfolio_rebalancing
from flask_restx import Resource
from finance.common.report import FundReport, StockAndEtfReport
from finance.common.calculate import get_portfolios, rebalance_portfolio
from finance.api.endpoints import run_func_against_dao
from functools import reduce
from dataclasses import dataclass
import logging.config

ns = api.namespace('report', description='Financial reports')
log = logging.getLogger(__name__)


@ns.route('/fund')
class FundPerformance(Resource):
    @api.marshal_list_with(fund_performance)
    def get(self):
        """
        Returns list of fund performance.
        """
        return run_func_against_dao(lambda dao: FundReport(dao, date.today()).positions)


@dataclass
class AllocItem:
    alloc: str
    ratio: float


@ns.route('/positions')
class Positions(Resource):
    @api.marshal_with(positions)
    def get(self):
        """
        Return a summary of all positions
        """
        def _alloc_auto_other(allocations):
            alloc = [AllocItem(x[0], x[1]) for x in allocations if x[0] != 'Other']
            total = reduce(lambda accu, x: accu + x.ratio, alloc, 0)
            if total > 100:
                log.error('Alloc over 100% : {}'.format(allocations))
            else:
                alloc.append(AllocItem('Other', 100 - total))
            for a in alloc:
                yield (a.alloc, a.ratio)

        def _get_position(dao, report):
            return [{'instrument': {'id': p['instrument'], 'name':p['symbol']},
                     'asset_allocation':
                         [{'asset': x[0],
                           'ratio': x[1]
                           } for x in dao.get_asset_allocation(instrument_id=p['instrument'])],
                     'country_allocation':
                         [{'country': x[0],
                           'ratio': x[1]
                           } for x in _alloc_auto_other(dao.get_country_allocation(instrument_id=p['instrument']))],
                     'region_allocation':
                         [{'region': x[0],
                           'ratio': x[1]
                           } for x in _alloc_auto_other(dao.get_region_allocation(instrument_id=p['instrument']))],
                     'ccy': p['ccy'],
                     'xccy': p['xccy'],
                     'shares': p['shares'],
                     'price': p['price'],
                     'capital': -p['liquidated']} for p in report if p['shares'] > 0]

        def _get_stock_etf_positions(dao):
            r = StockAndEtfReport(dao, date.today())
            return _get_position(dao, r.etf_position.positions), _get_position(dao, r.stock_position.positions)

        def _get_all(dao):
            # change to the same format as stock position
            # Japan mutual funds have different ways to calculate amount(口),
            # we simplify here by assigning total market value (scraped from broker's page) to price and keep share be 1
            funds_report_payload = FundReport(dao, date.today()).positions
            funds = {broker: [{'instrument': p.instrument_id,
                               'broker': p.broker,
                               'symbol': p.name,
                               'ccy': 'JPY',
                               'xccy': 1,
                               'shares': 1,
                               'price': p.value,
                               'liquidated': -p.capital
                               } for p in pp.values()] for broker, pp in funds_report_payload.items()}
            stocks = _get_stock_etf_positions(dao)
            return {'ETF': stocks[0],
                    'Stock': stocks[1],
                    'Funds': _get_position(dao, funds),
                    'Cash': [{'ccy': x[0], 'broker': x[1], 'balance': x[2], 'xccy': x[3]}
                             for x in dao.get_cash_balance()]}

        return run_func_against_dao(lambda dao: _get_all(dao))


@ns.route('/portfolios')
class Portfolios(Resource):
    @api.marshal_list_with(portfolio)
    def get(self):
        """
        Return a list of portfolios
        """
        portfolios = run_func_against_dao(lambda dao: get_portfolios(dao, date.today()))
        return [{'name': name, 'allocations': portfolio.to_dict('records')} for name, portfolio in portfolios]


@ns.route('/rebalance_portfolio/<string:name>/<int:new_fund>')
@api.doc(params={'name': 'Portfolio name'})
@api.doc(params={'new_fund': 'Amount of new fund to invest'})
class RebalancePortfolio(Resource):
    @api.marshal_with(portfolio_rebalancing)
    def get(self, name, new_fund=0):
        """
        Return a list of portfolio rebalancing plans.
        """
        r = run_func_against_dao(lambda dao: rebalance_portfolio(dao, date.today(), name, new_fund))

        plans = r['plans']
        if len(plans) == 0:
            return {}

        merged = r['merged']

        rebalancing = {
            'plans': [{"new_funds": p.delta_funds.sum(), "allocations": p.to_dict('records')} for p in plans],
            'merged': {} if merged is None else {"new_funds": merged.delta_funds.sum(), "allocations": merged.to_dict('records')}
        }
        return rebalancing
