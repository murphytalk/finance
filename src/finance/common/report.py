# -*- coding: utf-8 -*-
from dataclasses import dataclass
from json import dumps, encoder
from datetime import date

from finance.common.calculate import CalcPosition
from finance.common.dao.impl import ImplDao
from finance.common.model import Position
from finance.common.utils import epoch2date


# format float value in json
encoder.FLOAT_REPR = lambda o: format(o, '.2f')


class Report(object):
    def __init__(self, dao, date):
        self.i = dao.get_instrument_with_xccy_rate(date)

    @staticmethod
    def gen_price_with_xccy(org, currency, to_jpy_rate, rate_date):
        return {'ccy': currency, currency: org, 'JPY': org * to_jpy_rate, 'rate_date': str(rate_date)}

    @staticmethod
    def to_json(j):
        return dumps(j, indent=4, sort_keys=True)

    @staticmethod
    def to_json_packed(j):
        return dumps(j)

    @staticmethod
    def put(d, k, v):
        if k in d:
            d[k] += v
        else:
            d[k] = v


class StockReport(Report):
    def __init__(self, dao: ImplDao, date):
        super(self.__class__, self).__init__(dao, date)
        self.q = dao.get_stock_latest_quotes(date)
        self.stock_position = CalcPosition(date)
        self.stock_position.calc(dao)

    def stock_positions(self, positions=None):
        def calc_stock(instrument, position: Position):
            if instrument not in self.q:
                return
            vwap = position.VWAP()
            v = position.shares * self.q[instrument].price
            rpt = {
                'instrument': instrument,
                'symbol': position.name,
                'url': self.i[instrument].url,
                'ccy': self.i[instrument].currency,
                'xccy': self.i[instrument].xccy_rate,
                'shares': position.shares,
                'price': self.q[instrument].price,
                'value': v,
                'vwap': self.gen_price_with_xccy(vwap, self.i[instrument].currency,
                                                       self.i[instrument].xccy_rate, self.i[instrument].xccy_date),
                'liquidated': position.liquidated}

            t = self.i[instrument].instrument_type.name
            if t in positions:
                by_instrument = positions[t]
            else:
                by_instrument = []

            by_instrument.append(rpt)
            positions[t] = by_instrument

        if positions is None:
            positions = {}
        self.stock_position.dump(calc_stock)
        return positions


@dataclass
class FundPosition:
    broker: str
    name: str
    expense_ratio: float
    price: float
    amount: float
    capital: float
    value: float
    profit: float
    date: str
    instrument_id: int
    url: str


FundPositions = list[FundPosition]


class FundReport(Report):
    def __init__(self, dao: ImplDao, the_date):
        self.positions: FundPositions = [
            FundPosition(
                x['broker'],
                x['name'],
                x['expense_ratio'],
                x['price'],
                x['amount'],
                x['capital'],
                x['value'],
                x['profit'],
                str(epoch2date(x['date'])),
                x['instrument_id'],
                ['url']) for x in dao.get_funds_positions(the_date)
        ]


def get_pie_chart_data(generator):
    """
    return an array to be fed to HighCharts to plot pie chart
    generator should return a tuple of (name, ratio) for each iteration
    """
    return [{'name': e[0], 'y': e[1]} for e in generator]


def get_pie_chart_data_json(generator):
    return Report.to_json_packed(get_pie_chart_data(generator))


def asset_allocation(dao, instrument_id):
    return get_pie_chart_data_json(dao.get_asset_allocation(instrument_id=instrument_id))


def country_allocation(dao, instrument_id):
    return get_pie_chart_data_json(dao.get_country_allocation(instrument_id=instrument_id))


def region_allocation(dao, instrument_id):
    return get_pie_chart_data_json(dao.get_region_allocation(instrument_id=instrument_id))
