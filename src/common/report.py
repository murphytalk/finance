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


class Report:
    def __init__(self, dao, date):
        self.q = dao.get_stock_quote(date)
        self.i = dao.get_instrument_with_xccy_rate(date)
        self.stock_position = CalcPosition(date)
        self.stock_position.calc(dao)

    def gen_price_with_xccy(self, org, currency, to_jpy_rate, rate_date):
        return {'ccy': currency, currency: org, 'JPY': org * to_jpy_rate, 'rate_date': str(rate_date)}

    def list(self, rr=None):
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
            if t in rr:
                by_instrument = rr[t]
            else:
                by_instrument = []

            by_instrument.append(r)
            rr[t] = by_instrument

        if rr is None:
            rr = {}
        self.stock_position.dump(calc_stock)
        return rr

    def summary(self):
        pass

    @staticmethod
    def to_json(j):
        return dumps(j, indent=4, sort_keys=True)

    @staticmethod
    def to_json_packed(j):
        return dumps(j)


def raw_quote(dao):
    q = [[str(date.fromtimestamp(x['date'])), x['name'], x['price']] for x in
         dao.query('select * from stock_quote order by date desc')]
    return Report.to_json_packed({'data': q})


def raw_xccy(dao):
    q = [[str(date.fromtimestamp(x['date'])), x['From'], x['To'], x['rate']] for x in
         dao.query('select * from xccy_hist')]
    return Report.to_json_packed({'data': q})


def raw_trans(dao):
    q = [[str(date.fromtimestamp(x['date'])), x['name'], x['type'], x['price'], x['shares'], x['fee']] for x in
         dao.query('select date,name,type,price,shares,fee from stock_trans')]
    return Report.to_json_packed({'data': q})


if __name__ == "__main__":
    args, others = cmdline_args(sys.argv[1:])
    db = args['dbfile']

    if db is None:
        print 'Need a db file'
    else:
        dao = Dao(db)

        if 'report' in others:
            r = Report(dao, args['end_date'])
            print r.to_json(r.list())
        elif 'quote' in others:
            print Report.to_json(raw_quote(dao))
        elif 'xccy' in others:
            print Report.to_json(raw_xccy(dao))
        elif 'trans' in others:
            print Report.to_json(raw_trans(dao))

        dao.close()
