# -*- coding: utf-8 -*-
"""
Various calculations

parameter:
 -fxxxxxxx path to db file
 -i        do not update db file

"""
import sys,sqlite3
from datetime import date
from time import mktime
from utils import cmdline_args
from adapter import *


def iterate_transaction(db_path,start_date,end_date,callback):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    epoch1 = int(mktime(start_date.timetuple())+get_utc_offset())
    epoch2 = int(mktime(end_date.timetuple())+get_utc_offset())

    c.execute('select i.name,t.instrument,t.type,t.price,t.shares,t.fee,t.date from [transaction] t, instrument i where t.instrument = i.rowid and date >=? and date<=? order by date',(epoch1,epoch2))
    for f in c.fetchall():
        callback(f['instrument'],f['name'],f['type'],f['price'],f['shares'],f['fee'],f['date'])
    conn.close()


class Position:
    def __init__(self,instrument):
        self.instrument = instrument
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
        return "Instrument=%d,Shares=%d,Fee=%d,Liquidated=%d"%(self.instrument,self.shares,self.fee,self.liquidated)
        

class CalcPosition:
    def __init__(self,date1,date2):
        self.date1 = date1
        self.date2 = date2
        
    def calc(self,dbpath,no_update_db):
        def on_each_transaction(instrument,name,transaction_type,price,shares,fee,date):
            self.positions[name].transaction(transaction_type,price,shares,fee)
#            if not no_update_db:
                

            
        conn = sqlite3.connect(dbpath)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('select rowid,[name] from instrument where type = 2 or type = 1')
        conn.close
        self.positions = { x[1]:Position(x[0]) for x in c.fetchall() }
        
        iterate_transaction(dbpath,self.date1,self.date2,on_each_transaction)

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
