# -*- coding: utf-8 -*-
import sys
from json import dumps, encoder
from functools import reduce

from finance.common.calculate import CalcPosition
from finance.common.dao import Dao
from finance.common.utils import cmdline_args, epoch2date


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
    def __init__(self, dao, date):
        super(self.__class__, self).__init__(dao, date)
        self.q = dao.get_stock_latest_quotes(date)
        self.stock_position = CalcPosition(date)
        self.stock_position.calc(dao)

    def stock_positions(self, positions=None):
        def calc_stock(instrument, position):
            v = position.shares * self.q[instrument].price
            rpt = {
                'instrument': instrument, 'url': self.i[instrument].url, 'symbol': position.name,
                'shares': position.shares, 'price': self.q[instrument].price,
                'value': self.gen_price_with_xccy(v, self.i[instrument].currency, self.i[instrument].xccy_rate,
                                                  self.i[instrument].xccy_date),
                'liquidated': self.gen_price_with_xccy(position.liquidated, self.i[instrument].currency,
                                                       self.i[instrument].xccy_rate, self.i[instrument].xccy_date)}

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


class FundReport(Report):
    def __init__(self, dao, the_date):
        self.positions = [{
            'broker': x['broker'],
            'name': x['name'],
            'expense_ratio': x['expense_ratio'],
            'price': x['price'],
            'amount': x['amount'],
            'capital': x['capital'],
            'value': x['value'],
            'profit': x['profit'],
            'date': str(epoch2date(x['date'])),
            'instrument_id': x['instrument_id'],
            'url': x['url']} for x in dao.get_funds_positions(the_date)]


class SummaryReport(Report):
    def __init__(self, dao, the_date):
        def get_stock_positions(stock_positions):
            for v in stock_positions.values():
                for p in v:
                    yield (p['instrument'], p['value']['JPY'])

        def get_fund_positions(positions):
            for x in positions:
                yield (x['instrument_id'], x['value'])

        stock = StockReport(dao, the_date)
        funds = FundReport(dao, the_date)
        self.positions = [x for x in get_stock_positions(stock.stock_positions())] + [x for x in get_fund_positions(
            funds.positions)]

    def report(self, dao):
        def asset_class_generator(dao):
            asset_class = {}
            for instrument, value in self.positions:
                for asset, ratio in dao.get_asset_allocation(instrument_id=instrument):
                    self.put(asset_class, asset, value * ratio / 100)
            for k, v in asset_class.items():
                yield (k, v)

        def country_generator(dao):
            country = {}
            for instrument, value in self.positions:
                for rg, ratio in dao.get_country_allocation(instrument_id=instrument):
                    self.put(country, rg, value * ratio / 100)
            for k, v in country.items():
                yield (k, v)

        def region_generator(dao):
            region = {}
            for instrument, value in self.positions:
                for rg, ratio in dao.get_region_allocation(instrument_id=instrument):
                    self.put(region, rg, value * ratio / 100)
            for k, v in region.items():
                yield (k, v)

        # return {'total': reduce(lambda a, b: a[1]+b[1], self.positions),
        return {'total': reduce(lambda a, b: a + b, [x[1] for x in self.positions]),
                'asset': get_pie_chart_data(asset_class_generator(dao)),
                'country': get_pie_chart_data(country_generator(dao)),
                'region': get_pie_chart_data(region_generator(dao)),
                }


def get_pie_chart_data(generator):
    """
    return an array to be fed to HighCharts to plot pie chart
    generator should return a tuple of (name, ratio) for each iteration
    """
    data = []
    for e in generator:
        data.append({'name': e[0], 'y': e[1]})
    return data


def get_pie_chart_data_json(generator):
    return Report.to_json_packed(get_pie_chart_data(generator))


def asset_allocation(dao, instrument_id):
    return get_pie_chart_data_json(dao.get_asset_allocation(instrument_id=instrument_id))


def country_allocation(dao, instrument_id):
    return get_pie_chart_data_json(dao.get_country_allocation(instrument_id=instrument_id))


def region_allocation(dao, instrument_id):
    return get_pie_chart_data_json(dao.get_region_allocation(instrument_id=instrument_id))


def raw_xccy(dao):
    q = [[str(epoch2date(x['date'])), x['From'], x['To'], x['rate']] for x in
         dao.exec('SELECT * FROM xccy_hist')]
    return Report.to_json_packed({'data': q})


if __name__ == "__main__":
    # import codecs,locale
    # sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    args, others = cmdline_args(sys.argv[1:])
    db = args['dbfile']

    if db is None:
        print('Need a db file')
    else:
        dao = Dao(db)
        if 'stock' in others:
            r = StockReport(dao, args['end_date'])
            print(r.to_json(r.stock_positions()))
        elif 'fund' in others:
            r = FundReport(dao, args['end_date'])
        elif 'xccy' in others:
            print(Report.to_json(raw_xccy(dao)))
        elif 'sum' in others:
            r = SummaryReport(dao, args['end_date'])
            print(Report.to_json(r.report(dao)))

        dao.close()
