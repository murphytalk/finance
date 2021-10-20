#!/usr/bin/env python
"""
Various calculations

Calculations:
    500 buy-policy based on 550-day move

Usage:
    calculate.py 500 <ticker>...
    calculate.py -h | --help

Options:
    -h, --help        Show this screen

"""
if __name__ == "__main__":
    import sys
    import os.path
    from pathlib import Path

    # set up lib path
    p = Path(os.path.dirname(os.path.realpath(__file__)))
    root = str(p.parent.parent)
    sys.path.append(root)

from dataclasses import dataclass
from finance.common.const import STOCK_START_DATE
from finance.common.dao.impl import ImplDao
from finance.common.model import Position
from finance.common.const import REBALANCING_THRESHOLD
from functools import reduce
from yahoo_historical import Fetcher
from datetime import datetime
import pandas as pd
from numpy import float64


def associate_by_broker_then_instrument(item_generator,
                                        get_broker_from_item,
                                        get_instrument_from_item,
                                        create_new_stuff_from_item,
                                        on_item=None):
    by_broker = {}
    for item in item_generator:
        broker = get_broker_from_item(item)
        if broker in by_broker:
            by_instruments = by_broker[broker]
            instrument = get_instrument_from_item(item)
            if instrument in by_instruments:
                stuff = by_instruments[instrument]
            else:
                stuff = create_new_stuff_from_item(item)
                by_instruments[instrument] = stuff
        else:
            stuff = create_new_stuff_from_item(item)
            by_broker[broker] = {get_instrument_from_item(item): stuff}
        if on_item is not None:
            on_item(stuff, item)

    return by_broker


class CalcPosition:
    def __init__(self, date2, instrument_type: str = None):
        self.date1 = STOCK_START_DATE
        self.date2 = date2
        self.instrument_type = instrument_type
        # { broker => {instrument id => position} }
        self.positions: dict[str: dict[int, Position]] = {}

    def calc(self, dao: ImplDao):
        self.positions = associate_by_broker_then_instrument(
            dao.iterate_transaction(self.date1, self.date2, self.instrument_type),
            lambda item: item.broker,
            lambda item: item.instrument_id,
            lambda item: Position(item.instrument_id, item.instrument_name),
            lambda pos, t: pos.transaction(t.transaction_type, t.price, t.shares, t.fee)
        )

    def transform(self, transformer):
        return {broker: {instrument: transformer(instrument, position) for instrument, position in positions_by_instrument.items()} for broker, positions_by_instrument in self.positions.items()}


def get_portfolios(dao: ImplDao, at_which_day, name=None):
    def get_portfolio(portfolio_name, portfolio_allocation):
        closings = []
        targets = []
        positions = {}
        for instrument_id, instrument_name, percentage in portfolio_allocation:
            positions[instrument_id] = Position(instrument_id, instrument_name)
            quote = dao.get_stock_latest_quotes(
                at_which_day, instrument_name, instrument_id)
            closings.append((instrument_name, quote[instrument_id].price))
            targets.append((instrument_name, percentage))

        calc_pos = CalcPosition(at_which_day, positions)
        calc_pos.calc(dao)

        closings = pd.DataFrame(columns=['instrument', 'price'], data=closings)
        targets = pd.DataFrame(
            columns=['instrument', 'target_allocation'], data=targets)
        positions = pd.DataFrame(columns=['instrument', 'shares'], data=[
                                 [p.name, p.shares] for n, p in positions.items()])
        portfolio = reduce(lambda left, right: pd.merge(
            left, right, on='instrument'), [positions, closings, targets])
        portfolio['market_value'] = portfolio['shares'] * portfolio['price']
        total_value = portfolio.market_value.sum()
        portfolio['current_allocation'] = 100 * \
            portfolio['market_value'] / total_value
        return portfolio

    return [(name, get_portfolio(name, p)) for name, p in dao.get_portfolios(name).items()]


def rebalance_portfolio(dao, at_which_day, name, new_fund):
    def calc_cur_allocation(port):
        port['market_value'] = port['shares'] * port['price']
        total_value = port.market_value.sum()
        port['current_allocation'] = 100 * port['market_value'] / total_value
        port["deviation"] = port["target_allocation"] - \
            port["current_allocation"]

    portfolios = get_portfolios(dao, at_which_day, name)
    if len(portfolios) == 0:
        return None

    rebalancing_plans = []

    _, portfolio = portfolios[0]

    # do we need to do a no new money rebalancing first ?
    portfolio["deviation"] = abs(
        portfolio["target_allocation"] - portfolio["current_allocation"])
    if portfolio.deviation.max() >= REBALANCING_THRESHOLD:
        total = portfolio.market_value.sum()
        portfolio["target_market_value"] = total * \
            portfolio["target_allocation"] / 100
        portfolio["fund_to_transfer"] = portfolio["target_market_value"] - \
            portfolio["market_value"]
        portfolio["delta_shares"] = round(
            portfolio["fund_to_transfer"] / portfolio["price"])
        portfolio["delta_funds"] = portfolio["delta_shares"] * \
            portfolio["price"]
        portfolio["shares"] = portfolio["shares"] + portfolio["delta_shares"]

        calc_cur_allocation(portfolio)
        rebalancing_plans.append(portfolio.copy())

    if new_fund > 0:
        portfolio["fund_allocation"] = new_fund * \
            portfolio["target_allocation"] / 100
        portfolio["delta_shares"] = round(
            portfolio["fund_allocation"] / portfolio["price"])
        portfolio["delta_funds"] = portfolio["delta_shares"] * \
            portfolio["price"]
        portfolio["shares"] += portfolio["delta_shares"]

        calc_cur_allocation(portfolio)
        rebalancing_plans.append(portfolio.copy())

    if len(rebalancing_plans) > 1:
        portfolio["delta_shares"] += rebalancing_plans[0]["delta_shares"]
        portfolio["delta_funds"] = portfolio["delta_shares"] * \
            portfolio["price"]

    return {'plans': rebalancing_plans, 'merged': portfolio if len(rebalancing_plans) > 1 else None}


@dataclass
class Policy500DaysMove:
    ticker: str
    start_date: datetime
    end_date: datetime
    avg_closing: float64
    avg_diff: float
    # how many percentage of standard buy volume
    buy_scale: float


def calc_buying_by_500d_move(ticker, start_date, end_date):
    d1 = [start_date.year, start_date.month, start_date.day]
    d2 = [end_date.year, end_date.month, end_date.day]
    data = Fetcher(ticker, d1, d2)
    hist = data.get_historical()

    closings = hist['Close']
    # t_1_closing = closings[-1:]
    avg = closings.mean()
    # avg_diff = (t_1_closing - avg) / avg

    return Policy500DaysMove(ticker, start_date, end_date, avg)


if __name__ == "__main__":
    from docopt import docopt
    from datetime import timedelta

    args = docopt(__doc__)
    if args['500']:
        t_1 = datetime.today() - timedelta(days=1)
        d500 = t_1 - timedelta(days=500)
        for ticker in args['<ticker>']:
            print(calc_buying_by_500d_move(ticker, d500, t_1))
