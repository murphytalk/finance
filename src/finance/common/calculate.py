# -*- coding: utf-8 -*-
"""
Various calculations

parameter:
 -fxxxxxxx path to db file
 -i        do not update db file

"""
from finance.common.const import STOCK_START_DATE
from finance.common.model import Position, rebalance
from finance.common.utils import cmdline_args
from functools import reduce
import pandas as pd


class CalcPosition:
    def __init__(self, date2, positions=None):
        self.date1 = STOCK_START_DATE
        self.date2 = date2
        self.positions = positions

    def calc(self, dao):
        def on_each_transaction(instrument, name, transaction_type, price,
                                shares, fee, the_date):
            if instrument in self.positions:
                pos = self.positions[instrument]
                pos.transaction(transaction_type, price, shares, fee)

        if self.positions is None:
            self.positions = dao.populate_from_instruments(
                '(i.type = 2 or i.type = 1)',  # todo : get rid of magic numbers
                lambda instrument_id, name, tid, t, u, e: Position(
                    instrument_id, name))
        dao.iterate_transaction(self.date1, self.date2, on_each_transaction)

    def dump(self, callback=None):
        for k, v in self.positions.items():
            if callback is None:
                print(k, v)
            else:
                callback(k, v)


def get_portfolios(dao, at_which_day, name=None):
    def get_portfolio(portfolio_name, portfolio_allocation):
        closings = []
        targets = []
        positions = {}
        for instrument_id, instrument_name, percentage in portfolio_allocation:
            positions[instrument_id] = Position(instrument_id, instrument_name)
            quote = dao.get_stock_latest_quotes(at_which_day, instrument_name, instrument_id)
            closings.append((instrument_name, quote[instrument_id].price))
            targets.append((instrument_name, percentage))

        calc_pos = CalcPosition(at_which_day, positions)
        calc_pos.calc(dao)

        closings = pd.DataFrame(columns=['instrument', 'price'], data=closings)
        targets = pd.DataFrame(columns=['instrument', 'target_allocation'], data=targets)
        positions = pd.DataFrame(columns=['instrument', 'shares'], data=[[p.name, p.shares] for n, p in positions.items()])
        portfolio = reduce(lambda left, right: pd.merge(left, right, on='instrument'), [positions, closings, targets])
        portfolio['market_value'] = portfolio['shares'] * portfolio['price']
        total_value = portfolio.market_value.sum()
        portfolio['current_allocation'] = 100 * portfolio['market_value']/total_value
        return portfolio

    return [(name, get_portfolio(name, p)) for name, p in dao.get_portfolios(name).items()]
