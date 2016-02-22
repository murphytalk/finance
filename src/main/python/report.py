#!/usr/bin/python2
# -*- coding: utf-8 -*-
import sys
from utils import cmdline_args
from dao import Dao
from calculate import CalcPosition
from json import dumps,encoder

#format float value in json
encoder.FLOAT_REPR = lambda o: format(o, '.2f')

class Report:
    def __init__(self,dao,date):
        self.q = dao.get_stock_quote(date)
        self.i = dao.get_instrument_with_xccy_rate(date)
        self.stock_position = CalcPosition(date)
        self.stock_position.calc(dao)
    
    def gen_price_with_xccy(self,org,currency,to_jpy_rate,rate_date):
        return {currency:org,'JPY':org*to_jpy_rate,'rate_date':str(rate_date)}

    def list(self):
        def calc_stock(instrument,position):
            v = position.shares*self.q[instrument].price
            r = {}
            r['symbol'] = position.name
            r['shares'] = position.shares
            r['price']  = self.q[instrument].price
            r['value']  = self.gen_price_with_xccy(v,self.i[instrument].currency,self.i[instrument].xccy_rate,self.i[instrument].xccy_date)
            r['liquidated'] = self.gen_price_with_xccy(position.liquidated,self.i[instrument].currency,self.i[instrument].xccy_rate,self.i[instrument].xccy_date)
            rr.append(r)            

        rr = []
        self.stock_position.dump(calc_stock)
        return rr

    def summary(self):
        pass

    @staticmethod
    def to_json(j):
        return dumps(j,indent=4, sort_keys=True)

    @staticmethod
    def to_json_packed(j):
        return dumps(j)


if __name__ == "__main__":
    args,others = cmdline_args(sys.argv[1:])
    db = args['dbfile']

    if db is None:
        print 'Need a db file'
    else:
        dao = Dao(db)
        r = Report(dao,args['end_date'])
        print r.to_json(r.list())
        dao.close()
