# -*- coding: utf-8 -*-
import sys
from json import dumps, encoder
from datetime import date

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
                                                       self.i[instrument].xccy_rate, self.i[instrument].xccy_date),
                'vwap': self.gen_price_with_xccy(position.VWAP(), self.i[instrument].currency,
                                                       self.i[instrument].xccy_rate, self.i[instrument].xccy_date)
            }

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


class StockReport2(Report):
    def __init__(self, dao, date):
        super(self.__class__, self).__init__(dao, date)
        self.q = dao.get_stock_latest_quotes(date)
        self.stock_position = CalcPosition(date)
        self.stock_position.calc(dao)

    def stock_positions(self, positions=None):
        def calc_stock(instrument, position):
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
    def __init__(self, dao, the_date, filter_name):
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
        def get_allocation(get_allocation_func):
            allocation = {}
            for instrument, value in self.positions:
                for n, ratio in get_allocation_func(instrument_id=instrument):
                    self.put(allocation, n, value * ratio / 100)
            for k, v in allocation.items():
                yield (k, v)

        def asset_class(dao):
            return get_allocation(dao.get_asset_allocation)

        def country(dao):
            return get_allocation(dao.get_country_allocation)

        def region(dao):
            return get_allocation(dao.get_region_allocation)

        def stock_allocation(dao):
            """
            get stock instruments allocation, see /stock.json
            :param dao: dao
            :return (Stock,ETF)
            """
            def calc(stocks):
                return [{'symbol': x['symbol'],
                         'id': x['instrument'],
                         'ccy':x['value']['ccy'],
                         'value':x['value'][x['value']['ccy']],
                         'JPY':x['value']['JPY'],
                         'profit':x['value']['JPY'] - x['liquidated']['JPY']} for x in stocks if x['shares'] > 0]
            stocks = StockReport(dao, date.today()).stock_positions()
            return calc(stocks['Stock'] if 'Stock' in stocks else []), calc(stocks['ETF'] if 'ETF' in stocks else [])

        def funds_allocation(dao):
            return [{'symbol': x['name'],
                     'id': x['instrument_id'],
                     'ccy':'JPY',
                     'value':x['value'],
                     'JPY':x['value'],
                     'profit':x['profit']} for x in FundReport(dao, date.today()).positions]

        stock, etf = stock_allocation(dao)
        return {
            'asset': get_pie_chart_data(asset_class(dao)),
            'country': get_pie_chart_data(country(dao)),
            'region': get_pie_chart_data(region(dao)),
            'Stock': stock,
            'ETF': etf,
            'Funds': funds_allocation(dao)
        }



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
        elif 'sum' in others:
            r = SummaryReport(dao, args['end_date'])
            print(Report.to_json(r.report(dao)))

        dao.close()
