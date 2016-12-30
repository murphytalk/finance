# -*- coding: utf-8 -*-
import random
import sqlite3
from calendar import timegm

from finance.common.model import *
from finance.common.db import get_sql_scripts


class Raw:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

    def close(self):
        self.conn.close()

    def exec(self, sql, parameters=None):
        if parameters:
            self.c.execute(sql, parameters)
        else:
            self.c.execute(sql)
        return self.c.fetchall()

    def exec_many(self, sql, parameters):
        self.c.executemany(sql,parameters)
        return self.c.fetchall()


class Dao(Raw):
    def __init__(self, db_path):
        Raw.__init__(self, db_path)

    def iterate_transaction(self, start_date, end_date, callback):
        """
        iterate stock transactions, callback signature:
        callback(instrument id,instrument name,transaction type,price, shares,fee, date)
        """
        sql = ('SELECT i.name,t.instrument,t.type,t.price,t.shares,t.fee,t.date FROM [transaction] t, instrument i '
               'WHERE t.instrument = i.rowid AND date >=? AND date<=? ORDER BY date')
        epoch1 = int(timegm(start_date.timetuple()))
        epoch2 = int(timegm(end_date.timetuple()))

        for f in self.exec(sql, (epoch1, epoch2)):
            callback(f['instrument'], f['name'], f['type'], f['price'], f['shares'], f['fee'], f['date'])

    def populate_from_instruments(self, instrument_filter, create_new_obj_func=None):
        """
        Populate a dict {instrument id : user defined data type} by
        querying from table instrument , filter should be a valid SQL where clause

        create_new_obj_func signature:
        parameter:
          instrument id
          instrument name
        return:
          the new object
          :param create_new_obj_func:
          :param instrument_filter: a valid SQL where clause

        """
        c = create_new_obj_func if create_new_obj_func is not None else \
            lambda instrument_id, name, type_id, type_name, url, expense_ratio: Instrument.create(
                instrument_id, name, type_id, type_name, url, expense_ratio)
        sql = ('SELECT i.rowid,i.name,it.rowid AS type_id, it.type AS type, i.url, i.expense_ratio FROM '
               'instrument i,instrument_type it WHERE i.type = it.rowid')
        if instrument_filter is not None:
            sql = sql + ' and ' + instrument_filter
        return {x['rowid']: c(x['rowid'], x['name'], x['type_id'], x['type'], x['url'], x['expense_ratio'])
                for x in self.exec(sql)}

    def get_stock_quote(self, quote_date):
        """
        return a dict {instrument id : Quote}
        """
        epoch = int(timegm(quote_date.timetuple()))
        sql = ('SELECT q.instrument,i.name,q.price, q.date FROM quote q, instrument i '
               'WHERE date = (SELECT max(date) FROM quote WHERE  date<=?) AND q.instrument = i.rowid')

        r = self.exec(sql, (epoch,))
        return {x['instrument']: Quote(x['instrument'], x['name'], x['price'], x['date']) for x in r}

    def get_instrument_with_xccy_rate(self, the_date):
        """
        if the xccy rate on specified date does not exist, then use rate on the closet earlier date
        return a dict {instrument id : Instrument}
        """
        epoch = int(timegm(the_date.timetuple()))
        sql = ('SELECT '
               'i.rowid instrument,'
               'i.name,'
               'i.type instrument_type_id,'
               'a.type instrument_type,'
               'i.url,'
               'i.expense_ratio,'
               'c.name currency,'
               'ifnull(x.rate,1) rate,'
               'ifnull(x.date,?) rate_date ' #if instrument is denoted in JPY there is no xccy date
               'FROM instrument i '
               'JOIN instrument_type a ON i.type = a.rowid '
               'JOIN currency c ON i.currency = c.rowid '
               'LEFT JOIN ( SELECT * FROM xccy_hist WHERE date = (SELECT max(date) FROM xccy_hist WHERE date<=?)) x '
               'ON i.currency = x.from_id')

        return {
            x['instrument']: Instrument.create(
            x['instrument'],
            x['name'],
            x['instrument_type_id'],
            x['instrument_type'],
            x['url'],
            x['expense_ratio'],
            x['currency'],
            x['rate'],
            x['rate_date']) for x in self.exec(sql, (epoch, epoch))}

    def get_funds_positions(self, the_date):
        """
        Query funds performance view, query the latest day's data no late than give date,
        return a generator which generates a stream of (broker,name,price,amount,capital,value,profit,date in epoch)
        """
        sql = ('SELECT broker,name,instrument_id,url,expense_ratio,amount,price,value,profit,capital,date '
               'FROM fund_performance WHERE '
               'date = (SELECT max(date) FROM fund_performance WHERE date<= :date)')
        epoch = int(timegm(the_date.timetuple()))
        for r in self.exec(sql, {'date': epoch}):
            yield (r['broker'], r['name'], r['expense_ratio'], r['price'], r['amount'], r['capital'],
                   r['value'], r['profit'], r['date'], r['instrument_id'], r['url'])

    def get_asset_allocation(self, instrument_id):
        sql = ('SELECT t.type,a.ratio FROM asset_allocation a, asset t WHERE a.instrument = ? AND a.asset=t.rowid '
               'ORDER BY a.asset')
        for r in self.exec(sql, (int(instrument_id),)):
            yield (r['type'], r['ratio'])

    def get_region_allocation(self, instrument_id):
        sql = ('SELECT t.name,a.ratio FROM region_allocation a, region t WHERE a.instrument = ? AND a.region=t.rowid '
               'ORDER BY a.region')
        for r in self.exec(sql, (int(instrument_id),)):
            yield (r['name'], r['ratio'])


def factory(db_file_path):
    """
    create a Dao object from db path.
    If db path is None, a FakeDao object will be created
    """
    if db_file_path is None:
        class FakeDao(Dao):
            """
            randomly generate static and market data instead of reading from DB

            STOCK_NUM - how many stocks to generate
            """
            # 2014-1-1
            DAY1 = 1388534400
            STOCK_NUM = 20
            URL = 'http://finance.yahoo.com/'

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
            def gen_expense_ration(cls):
                return random.uniform(0.1, 3)

            @classmethod
            def gen_price(cls, min_price, max_price):
                return random.uniform(min_price, max_price)

            def __init__(self, db_path):
                self.stocks = {}
                instrument_id = 1
                while len(self.stocks) < FakeDao.STOCK_NUM:
                    symbol = FakeDao.gen_stock_symbol()
                    if symbol in self.stocks:
                        continue
                    self.stocks[instrument_id] = Instrument(instrument_id, symbol, random.choice(
                        (InstrumentType(1, 'Stock'), InstrumentType(2, 'ETF'))))
                    instrument_id += 1

                # create the DB in memory and then populate random generated data
                Dao.__init__(self, ":memory:")
                # run the SQL script
                self.conn.executescript(get_sql_scripts())

                # read meta data
                asset = {x['ROWID']: x['type'] for x in self.exec('select ROWID,type from asset')}
                asset_by_type = {v: k for k, v in asset}

                broker = {x['name']: x['ROWID'] for x in self.exec('select ROWID,name from broker')}
                currency = {x['name']: x['ROWID'] for x in self.exec('select ROWID,name from currency')}
                region = {x['ROWID']: x['name'] for x in self.exec('select ROWID,name from region')}
                instrument_type = {x['type']: x['ROWID'] for x in self.exec('select ROWID,type from instrument_type')}

                # randomly generate Stock/ETF
                while len(self.stocks) < FakeDao.STOCK_NUM:
                    symbol = FakeDao.gen_stock_symbol()

                    row = self.exec('select count(*) as c from instrument where name=?', (symbol,))
                    if row['c'] > 0:
                        continue

                    self.stocks[instrument_id] = Instrument(instrument_id, symbol, random.choice(
                        (InstrumentType(1, 'Stock'), InstrumentType(2, 'ETF'))))



            def q_transaction(self):
                l = []

                for s in self.stocks.values():
                    # buy >1000 shares for each on day one
                    l.append({'instrument': s.id,
                              'name': s.name,
                              'type': 'BUY',
                              'price': FakeDao.gen_price(20, 1000),
                              'shares': random.randint(1000, 2000),
                              'fee': FakeDao.gen_price(5, 20),
                              'date': FakeDao.DAY1
                              })

                    # sell < 400 for each one we bought on a random day after day one
                    for i in range(2):
                        l.append({'instrument': s.id,
                                  'name': s.name,
                                  'type': 'SELL',
                                  'price': FakeDao.gen_price(20, 1000),
                                  'shares': random.randint(100, 400),
                                  'fee': FakeDao.gen_price(5, 20),
                                  'date': FakeDao.gen_date()
                                  })

                return l

            def q_instrument(self):
                return ({'rowid': s.id,
                         'name': s.name,
                         'type_id': s.instrument_type.id,
                         'type': s.instrument_type.name,
                         'url': FakeDao.URL,
                         'expense_ratio': FakeDao.gen_expense_ration()
                         } for s in self.stocks.values())

            def q_quote(self):
                return (
                    {'instrument': s.id, 'name': s.name, 'price': FakeDao.gen_price(20, 1000),
                     'date': FakeDao.today}
                    for s
                    in
                    self.stocks.values())

            def q_instrument_xccy(self):
                return ({'instrument': s.id,
                         'name': s.name,
                         'instrument_type_id': s.instrument_type.id,
                         'instrument_type': s.instrument_type.name,
                         'url': FakeDao.URL,
                         'currency': 'USD',
                         'expense_ratio': FakeDao.gen_expense_ration(),
                         'rate': FakeDao.gen_price(1, 130),
                         'rate_date': FakeDao.today
                         } for s in self.stocks.values())

            @staticmethod
            def q_region_allocation():
                return ({'name': r, 'ratio': random.randint(10, 30)}
                        for r in ('US', 'Europe', 'Japan', 'Emerging Market'))

            @staticmethod
            def q_asset_allocation():
                return ({'type': r, 'ratio': random.randint(10, 30)}
                        for r in ('Bond', 'Stock', 'Cash'))

        return FakeDao(db_file_path)
    else:
        return Dao(db_file_path)


if __name__ == "__main__":
    d = factory(None)

    d.exec_many("insert into region VALUES (?)", [("US",), ("Europe",), ("Japan",), ("Emerge",)])

    for f in d.exec("select ROWID,name from region"):

        print("%d\t%s"%(f["ROWID"], f["name"]))
