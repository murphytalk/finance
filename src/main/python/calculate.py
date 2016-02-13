# -*- coding: utf-8 -*-
"""
Various calculations

parameter:
 -fxxxxxxx path to db file
 -i        do not update db file

"""
import sys,sqlite3
from datetime import date
from utils import cmdline_args
from adapter import *
from dao import Dao
from model import Position
from const import STOCK_START_DATE
        
class CalcPosition:
    def __init__(self,date2):
        self.date1 = STOCK_START_DATE
        self.date2 = date2
        
    def calc(self,dbpath):
        def on_each_transaction(instrument,name,transaction_type,price,shares,fee,date):
            pos = self.positions[instrument]
            pos.transaction(transaction_type,price,shares,fee)
            #d.save_stock_position(pos,date)

        d = Dao(dbpath)
        self.positions = d.populate_from_intruments('type = 2 or type = 1',lambda id,name : Position(id,name))
        d.iterate_transaction(self.date1,self.date2,on_each_transaction)

        d.close()

    def dump(self):
        for k,v in self.positions.iteritems():
            print k,v
    
if __name__ == '__main__':

    args,others = cmdline_args(sys.argv[1:])
    db = args['dbfile']

    if db is None:
        print 'Need a db file'
    else:
        c = CalcPosition(args['end_date'])
        c.calc(db)
        c.dump()
