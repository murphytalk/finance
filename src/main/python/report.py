#!/usr/bin/python2
# -*- coding: utf-8 -*-
import sys
from utils import cmdline_args
from dao import Dao
from calculate import CalcPosition

def stock_report(dao,date):
    def calc(instrument,position):
        p,d = dao.get_stock_quote()
        r[instrument] = ()

    r = {}    
    c = CalcPosition(date)
    c.calc(dao)
    c.dump(calc)

if __name__ == "__main__":
    args,others = cmdline_args(sys.argv[1:])
    db = args['dbfile']

    if db is None:
        print 'Need a db file'
    else:
        dao = Dao(db)
        stock_report(dao,args['end_date'])
        dao.close()
