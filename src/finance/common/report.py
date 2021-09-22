# -*- coding: utf-8 -*-
from dataclasses import dataclass
from json import dumps, encoder
from datetime import date

from finance.common.calculate import CalcPosition, associate_by_broker_then_instrument
from finance.common.dao.impl import ImplDao
from finance.common.model import Position
from finance.common.utils import epoch2date


# format float value in json
encoder.FLOAT_REPR = lambda o: format(o, '.2f')


class Report(object):
    def __init__(self, dao: ImplDao, d: date):
        self.i = dao.get_instrument_with_xccy_rate(d)

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


@dataclass
class PositionReportPayload:
    instrument: int
    symbol: str
    ccy: str
    xccy: float
    shares: float
    price: float
    liquidated: float


PositionReportPayloadByBroker = dict[str, dict[int, PositionReportPayload]]


class StockAndEtfReport(Report):
    def __init__(self, dao: ImplDao, d: date):
        super(self.__class__, self).__init__(dao, date)
        self.stock_position = CalcPosition(date, 'Stock')
        self.stock_position.calc(dao)
        self.etf_position = CalcPosition(date, 'ETF')
        self.etf_position.calc(dao)

    def get_position_report(self, pos: CalcPosition) -> PositionReportPayloadByBroker:
        def calc_stock(instrument: int, position: Position):
            PositionReportPayload(
                instrument,
                position.name,
                self.i[instrument].currency,
                self.i[instrument].xccy_rate,
                position.shares,
                self.q[instrument].price,
                position.liquidated,
            )
        return pos.transform(calc_stock)

    def get_stock_position_report(self):
        return self.get_position_report(self.stock_position)

    def get_etf_position_report(self):
        return self.get_position_report(self.etf_position)


@dataclass
class FundPositioPayload:
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


FundPositionPayloadByBroker = dict[str, dict[int, FundPositioPayload]]


class FundReport(Report):
    def __init__(self, dao: ImplDao, the_date):
        self.positions: FundPositionPayloadByBroker = associate_by_broker_then_instrument(
            dao.get_funds_positions(the_date),
            lambda item: item['broker'],
            lambda item: item['instrument_id'],
            lambda x: FundPositioPayload(
                x['name'],
                x['expense_ratio'],
                x['price'],
                x['amount'],
                x['capital'],
                x['value'],
                x['profit'],
                str(epoch2date(x['date'])),
                x['instrument_id'],
                x['url'])
        )

    def get_position_report(self):
        # change to the same format as stock position
        # Japan mutual funds have different ways to calculate amount(口),
        # we simplify here by assigning total market value (scraped from broker's page) to price and keep share be 1
        return {broker: [PositionReportPayload(position.instrument_id, position.name, 'JPY', 1.0, 1, position.value, -position.capital) for position in positions_by_instrument.values()] for broker, positions_by_instrument in self.positions.items()}


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
