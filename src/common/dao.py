# -*- coding: utf-8 -*-
import random
import sqlite3
from time import mktime

from model import *
from utils import get_utc_offset


class Raw:
    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

    def close(self):
        self.conn.close()

    def query(self, sql, parameters=None):
        if parameters:
            self.c.execute(sql, parameters)
        else:
            self.c.execute(sql)
        return self.c.fetchall()


class Dao(Raw):
    def __init__(self, dbpath):
        Raw.__init__(self, dbpath)

    def iterate_transaction(self, start_date, end_date, callback):
        """
        iterate stock transactions, callback signature:
        callback(instrument id,instrument name,transaction type,price, shares,fee, date)
        """
        sql = """
SELECT i.name,t.instrument,t.type,t.price,t.shares,t.fee,t.date FROM [transaction] t, instrument i
WHERE t.instrument = i.rowid AND date >=? AND date<=? ORDER BY date
"""
        epoch1 = int(mktime(start_date.timetuple()) + get_utc_offset())
        epoch2 = int(mktime(end_date.timetuple()) + get_utc_offset())

        for f in self.query(sql,(epoch1, epoch2)):
            callback(f['instrument'], f['name'], f['type'], f['price'], f['shares'], f['fee'], f['date'])

    def populate_from_instruments(self, filter, create_new_obj_func = None):
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
        c = create_new_obj_func if create_new_obj_func is not None else lambda id,name,type_id,type_name : Instrument(id,name,type_id,type_name)
        sql = 'SELECT i.rowid,i.name,it.rowid AS type_id, it.type AS type FROM instrument i,instrument_type it WHERE i.type = it.rowid'
        if filter is not None:
            sql = sql + ' and ' + filter
        return {x['rowid']: c(x['rowid'], x['name'],x['type_id'],x['type']) for x in self.query(sql)}

    def get_stock_quote(self, date):
        """
        return a dict {instrument id : Quote}
        """
        epoch = int(mktime(date.timetuple()) + get_utc_offset())
        sql = """
select 
q.instrument,i.name,q.price, q.date from quote q, instrument i 
where date = (select max(date) from quote where  date<=?) and
q.instrument = i.rowid"""

        r = self.query(sql, (epoch,))
        return {x['instrument']: Quote(x['instrument'], x['name'], x['price'], x['date']) for x in r}

    def get_instrument_with_xccy_rate(self, date):
        """
        if the xccy rate on specified date does not exist, then use rate on the closet earlier date
        return a dict {instrument id : Instrument}
        """
        epoch = int(mktime(date.timetuple()) + get_utc_offset())
        sql = """
select
i.rowid instrument, 
i.name, 
i.type instrument_type_id, 
a.type instrument_type, 
c.name currency, 
ifnull(x.rate,1) rate,
ifnull(x.date,0) rate_date
from instrument i
join instrument_type a on i.type = a.rowid
join currency c on i.currency = c.rowid
left join ( select * from xccy_hist where date = (select max(date) from xccy_hist where date<=?)) x 
on i.currency = x.from_id
"""

        return {x['instrument']: Instrument(x['instrument'],
                                            x['name'],
                                            x['instrument_type_id'],
                                            x['instrument_type'],
                                            x['currency'],
                                            x['rate'],
                                            x['rate_date']) for x in self.query(sql, (epoch,))}

    def get_funds_positions(self, date):
        """
        Query funds performance view, query the latest day's data no late than give date,
        return a generator which generates a stream of (broker,name,price,amount,capital,value,profit,date in epoch)
        """
        sql = """
select broker,name,amount,price,value,profit,capital,date from fund_performance where
date = (select max(date) from fund_performance where date<= :date)
"""
        for r in self.query(sql, {'date': date}):
            yield (r['broker'], r['name'], r['price'], r['amount'], r['capital'], r['value'], r['profit'], r['date'])


class FakeDao(Dao):
    """
    randomly generate static and market data instead of reading from DB

    STOCK_NUM - how many stocks to generate
    """

    DAY1 = 1388534400
    STOCK_NUM = 10

    class Stock:
        def __init__(self, instrument, name, itype):
            self.instrument = instrument
            self.name = name
            self.type = itype

    from time import time

    today = int(time())

    @classmethod
    def gen_stock_symbol(cls):
        """
        generate a 4 letter symbol
        """

        def c():
            return chr(random.randint(ord('A'), ord('Z')))

        s = ''
        for i in range(4):
            s += c()
        return s

    @classmethod
    def gen_date(cls):
        """
        generate a date between 2014-1-1 to today
        """
        return random.randint(FakeDao.DAY1, FakeDao.today)

    @classmethod
    def gen_price(cls, min, max):
        return random.uniform(min, max);

    def __init__(self, dbpath):
        self.stocks = {}
        instrument_id = 1
        while len(self.stocks) < FakeDao.STOCK_NUM:
            symbol = FakeDao.gen_stock_symbol()
            if symbol in self.stocks:
                continue
            self.stocks[instrument_id] = FakeDao.Stock(instrument_id, symbol, random.choice(
                (InstrumentType(1, 'Stock'), InstrumentType(2, 'ETF'))))
            instrument_id += 1

    def close(self):
        pass

    def q_transaction(self):
        l = []

        for s in self.stocks.values():
            # buy >1000 shares for each on day one
            l.append({'instrument': s.instrument,
                      'name': s.name,
                      'type': 'BUY',
                      'price': FakeDao.gen_price(20, 1000),
                      'shares': random.randint(1000, 2000),
                      'fee': FakeDao.gen_price(5, 20),
                      'date': FakeDao.DAY1
                      })

            # sell < 400 twich for each on random day after day one
            for i in range(2):
                l.append({'instrument': s.instrument,
                          'name': s.name,
                          'type': 'SELL',
                          'price': FakeDao.gen_price(20, 1000),
                          'shares': random.randint(100, 400),
                          'fee': FakeDao.gen_price(5, 20),
                          'date': FakeDao.gen_date()
                          })

        return l

    def q_instrument(self):
        return ({'ROWID': s.instrument, 'NAME': s.name} for s in self.stocks.values())

    def q_quote(self):
        return (
        {'instrument': s.instrument, 'name': s.name, 'price': FakeDao.gen_price(20, 1000), 'date': FakeDao.today} for s
        in
        self.stocks.values())

    def q_instrument_xccy(self):
        return ({'instrument': s.instrument,
                 'name': s.name,
                 'instrument_type_id': s.type.id,
                 'instrument_type': s.type.name,
                 'currency': 'USD',
                 'rate': FakeDao.gen_price(1, 130),
                 'rate_date': FakeDao.today
                 } for s in self.stocks.values())

    def query(self, sql, parameters=None):
        # identify the query,use regex?
        if sql.find('[transaction] t, instrument i') > 0:
            q_func = self.q_transaction
        elif sql.find('FROM INSTRUMENT') > 0:
            q_func = self.q_instrument
        elif sql.find('select max(date) from quote') > 0:
            q_func = self.q_quote
        elif sql.find('ifnull(x.rate,1) rate') > 0:
            q_func = self.q_instrument_xccy
        else:
            q_func = None

        if q_func is not None:
            return q_func()
        else:
            return None


def factory(dbpath):
    """
    create a Dao object from db path.
    If db path is None, a FakeDao object will be created
    """
    return FakeDao(dbpath) if (dbpath is None) else Dao(dbpath)
