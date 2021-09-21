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
    instrument_type: str
    url: str
    ccy: str
    xccy: float
    shares: float
    price: float
    value: float
    vwap: float
    liquidated: float


PositionReportPayloadByBroker = dict[str, dict[int, list[PositionReportPayload]]]


class StockAndEtfReport(Report):
    def __init__(self, dao: ImplDao, d: date):
        super(self.__class__, self).__init__(dao, date)
        self.q = dao.get_stock_latest_quotes(date)
        self.stock_position = CalcPosition(date, 'Stock')
        self.stock_position.calc(dao)
        self.etf_position = CalcPosition(date, 'ETF')
        self.etf_position.calc(dao)

    def get_report(self, pos: CalcPosition) -> PositionReportPayloadByBroker:
        def calc_stock(instrument: int, position: Position):
            if instrument not in self.q:
                raise RuntimeError(f'unknown instrument id {instrument}')

            vwap = position.VWAP()
            v = position.shares * self.q[instrument].price
            PositionReportPayload(
                instrument,
                position.name,
                self.i[instrument].instrument_type.name,
                self.i[instrument].url,
                self.i[instrument].currency,
                self.i[instrument].xccy_rate,
                position.shares,
                self.q[instrument].price,
                v,
                # self.gen_price_with_xccy(vwap, self.i[instrument].currency, self.i[instrument].xccy_rate, self.i[instrument].xccy_date),
                vwap,
                position.liquidated
            )
        return pos.transform(calc_stock)

    def get_stock_report(self):
        return self.get_report(self.stock_position)

    def get_etf_report(self):
        return self.get_report(self.etf_position)


@dataclass
class FundPositionReportPayload:
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


FundPositionReportPayloadByBroker = dict[str, dict[int, list[FundPositionReportPayload]]]


class FundReport(Report):
    def __init__(self, dao: ImplDao, the_date):
        self.positions = associate_by_broker_then_instrument(
            dao.get_funds_positions(the_date),
            lambda item: item['broker'],
            lambda item: item['instrument_id'],
            lambda x: FundPositionReportPayload(
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
                x['url'])
        )


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
