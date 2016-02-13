# -*- coding: utf-8 -*-
import sqlite3
from time import mktime
from utils import get_utc_offset
from model import Position

class Dao:
    def __init__(self,dbpath):
        self.conn = sqlite3.connect(dbpath)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

    def close(self):
        self.conn.close()
        
    def iterate_transaction(self,start_date,end_date,callback):
        """
        iterate stock transactions, callback signature:
        callback(instrument id,instrument name,transaction type,price, shares,fee, date)
        """
        epoch1 = int(mktime(start_date.timetuple())+get_utc_offset())
        epoch2 = int(mktime(end_date.timetuple())+get_utc_offset())
    
        self.c.execute('select i.name,t.instrument,t.type,t.price,t.shares,t.fee,t.date from [transaction] t, instrument i where t.instrument = i.rowid and date >=? and date<=? order by date',(epoch1,epoch2))
        for f in self.c.fetchall():
            callback(f['instrument'],f['name'],f['type'],f['price'],f['shares'],f['fee'],f['date'])
        
    def populate_from_intruments(self,filter,create_new_obj_func):
        """
        Populate a dict {instrument id : user defined data type} by
        querying from table instrument , filter should be a valid SQL where clause
        
        create_new_obj_func signature:
        parameter:
          instrument id
          instrument name
        return:
          the new object

        """
        sql = 'SELECT ROWID,[NAME] FROM INSTRUMENT'
        if filter is not None:
            sql = sql + ' where ' + filter
        self.c.execute(sql)
        return {x[0]:create_new_obj_func(x[0],x[1]) for x in self.c.fetchall()}


    def save_stock_position(self,position,date):
        #sql = "INSERT INTO stock_position VALUES ()"
        print "%s,[%s],%d"%(date,position.name,position.shares)
