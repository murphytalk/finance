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

class Position:
    def __init__(self,instrument,name):
        self.instrument = instrument
        self.name = name
        self.shares = 0
        self.liquidated = 0 # negative value => money(original value) still in market
        self.fee = 0

    def transaction(self,trans_type,price,shares,fee):
            if trans_type == 'SPLIT':
                # 1 to N share split, here price is the N
                self.shares = self.shares * price 
            else:
                s = shares if trans_type == 'BUY' else -1*shares
                self.shares = self.shares + s
                self.liquidated = self.liquidated - price*s
                self.fee = self.fee + fee

    def __str__(self):
        return "Instrument=%d,Name=%s,Shares=%d,Fee=%d,Liquidated=%d"%(self.instrument,self.name,self.shares,self.fee,self.liquidated)
        
class CalcPosition:
    def __init__(self,date1,date2):
        self.date1 = date1
        self.date2 = date2
        
    def calc(self,dbpath,no_update_db):
        def on_each_transaction(instrument,name,transaction_type,price,shares,fee,date):
            self.positions[instrument].transaction(transaction_type,price,shares,fee)
#            if not no_update_db:
                

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
        c = CalcPosition(date(2014,1,1),args['end_date'])
        c.calc(db,'-i' in others)
        c.dump()
