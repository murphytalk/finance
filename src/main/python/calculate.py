# -*- coding: utf-8 -*-
"""
Various calculations
"""
import sys,sqlite3,datetime
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


class CalcPosition:
    def __init__(self,date1,date2):
        self.date1 = date1
        self.date2 = date2
        
    def calc(self,dbpath):
        def on_each_transaction(instrument,name,transaction_type,price,shares,fee,date):
            if transaction_type == 'SPLIT':
                self.positions[name] = self.positions[name] * price
            else:
                self.positions[name] = self.positions[name] + (shares if transaction_type == 'BUY' else -1*shares)

        conn = sqlite3.connect(dbpath)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('select rowid,[name] from instrument where type = 2 or type = 1')
        conn.close
        self.positions = { x[1]:0 for x in c.fetchall() }
        
        iterate_transaction(dbpath,self.date1,self.date2,on_each_transaction)

    def dump(self):
        for k,v in self.positions.iteritems():
            print k,v
    
if __name__ == '__main__':

    args,providers = cmdline_args(sys.argv[1:])
    db = args['dbfile']

    if db is None:
        print 'Need a db file'
    else:
        c = CalcPosition(args['start_date'],args['end_date'])
        c.calc(db)
        c.dump()
