#!/usr/bin/python2
# -*- coding: utf-8 -*-
import sys
from utils import cmdline_args
from dao import Dao
from calculate import CalcPosition

def xccy(org,currency,to_jpy_rate,rate_date):
    return "{}={},JPY={}({})".format(currency,org,org*to_jpy_rate,rate_date)

class Report:
    def __init__(self,dao,date):
        self.q = dao.get_stock_quote(date)
        self.i = dao.get_instrument_with_xccy_rate(date)
        self.stock_position = CalcPosition(date)
        self.stock_position.calc(dao)
    
    def list(self):
        def calc_stock(instrument,position):
            v = position.shares*self.q[instrument].price
            print "Symbol={},Shares={},Price={}({}),Value=[{}],Liquidated=[{}]".format(position.name,
                                                                                       position.shares,
                                                                                       self.q[instrument].price,
                                                                                       self.q[instrument].date,
                                                                                       xccy(v,self.i[instrument].currency,self.i[instrument].xccy_rate,self.i[instrument].xccy_date),
                                                                                       xccy(position.liquidated,self.i[instrument].currency,self.i[instrument].xccy_rate,self.i[instrument].xccy_date))
        self.stock_position.dump(calc_stock)

    def summary(self):
        pass


if __name__ == "__main__":
    args,others = cmdline_args(sys.argv[1:])
    db = args['dbfile']

    if db is None:
        print 'Need a db file'
    else:
        dao = Dao(db)
        r = Report(dao,args['end_date'])
        r.list()
        dao.close()
