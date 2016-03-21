#!/usr/bin/python2
# -*- coding: utf-8 -*-
import sys
from utils import cmdline_args
from dao import Dao
from calculate import CalcPosition
from json import dumps, encoder
from datetime import date

# format float value in json
encoder.FLOAT_REPR = lambda o: format(o, '.2f')


class Report(object):
    def __init__(self, dao, date):
        self.i = dao.get_instrument_with_xccy_rate(date)

    def gen_price_with_xccy(self, org, currency, to_jpy_rate, rate_date):
        return {'ccy': currency, currency: org, 'JPY': org * to_jpy_rate, 'rate_date': str(rate_date)}

    @staticmethod
    def to_json(j):
        return dumps(j, indent=4, sort_keys=True)

    @staticmethod
    def to_json_packed(j):
        return dumps(j)


class StockReport(Report):
    def __init__(self, dao, date):
        super(self.__class__, self).__init__(dao, date)
        self.q = dao.get_stock_quote(date)
        self.stock_position = CalcPosition(date)
        self.stock_position.calc(dao)

    def stock_positions(self, positions=None):
        def calc_stock(instrument, position):
            v = position.shares * self.q[instrument].price
            r = {}
            r['symbol'] = position.name
            r['shares'] = position.shares
            r['price'] = self.q[instrument].price
            r['value'] = self.gen_price_with_xccy(v, self.i[instrument].currency, self.i[instrument].xccy_rate,
                                                  self.i[instrument].xccy_date)
            r['liquidated'] = self.gen_price_with_xccy(position.liquidated, self.i[instrument].currency,
                                                       self.i[instrument].xccy_rate, self.i[instrument].xccy_date)

            t = self.i[instrument].instrument_type.name
            if t in positions:
                by_instrument = positions[t]
            else:
                by_instrument = []

            by_instrument.append(r)
            positions[t] = by_instrument

        if positions is None:
            positions = {}
        self.stock_position.dump(calc_stock)
        return positions


class FundReport(Report):
    def __init__(self, dao, the_date):
        self.positions = [[x[0], x[1], x[2], x[3], x[4], x[5], x[6], str(the_date.fromtimestamp(x[7])), x[8], x[9]]
                          for x in dao.get_funds_positions(the_date)]

def asset_allocation(dao, instrument_id):
    data = []
    for e in [x for x in dao.get_asset_allocation(instrument_id)]:
        data.append({'name':e[0], 'y':e[1]})
    return Report.to_json_packed(data)

def raw_quote(dao):
    q = [[str(date.fromtimestamp(x['date'])), x['name'], x['price']] for x in
         dao.query('SELECT * FROM stock_quote ORDER BY date DESC')]
    return Report.to_json_packed({'data': q})


def raw_xccy(dao):
    q = [[str(date.fromtimestamp(x['date'])), x['From'], x['To'], x['rate']] for x in
         dao.query('SELECT * FROM xccy_hist')]
    return Report.to_json_packed({'data': q})


def raw_trans(dao):
    q = [[str(date.fromtimestamp(x['date'])), x['name'], x['type'], x['price'], x['shares'], x['fee']] for x in
         dao.query('SELECT date,name,type,price,shares,fee FROM stock_trans')]
    return Report.to_json_packed({'data': q})


if __name__ == "__main__":
    # import codecs,locale
    # sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    args, others = cmdline_args(sys.argv[1:])
    db = args['dbfile']

    if db is None:
        print 'Need a db file'
    else:
        dao = Dao(db)

        if 'stock' in others:
            r = StockReport(dao, args['end_date'])
            print r.to_json(r.stock_positions())
        elif 'fund' in others:
            r = FundReport(dao, args['end_date'])
        elif 'quote' in others:
            print Report.to_json(raw_quote(dao))
        elif 'xccy' in others:
            print Report.to_json(raw_xccy(dao))
        elif 'trans' in others:
            print Report.to_json(raw_trans(dao))

        dao.close()
