# -*- coding: utf-8 -*-
import random
import sqlite3
from calendar import timegm

from finance.common.model import *
from finance.common.db import get_sql_scripts


class Dao:
    class Raw:
        def __init__(self, db_path):
            self.db_path = db_path
            self.conn = None
            self.c = None

        def connect(self):
            self.conn = sqlite3.connect(self.db_path)
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
            self.c.executemany(sql, parameters)
            return self.c.fetchall()

    class RealDao(Raw):
        def __init__(self, db_path):
            super().__init__(db_path)

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
                   'ifnull(x.date,?) rate_date '  # if instrument is denoted in JPY there is no xccy date
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
            sql = (
            'SELECT t.name,a.ratio FROM region_allocation a, region t WHERE a.instrument = ? AND a.region=t.rowid '
            'ORDER BY a.region')
            for r in self.exec(sql, (int(instrument_id),)):
                yield (r['name'], r['ratio'])

    class FakeDao(RealDao):
        """
        randomly generate static and market data instead of reading from DB

        STOCK_NUM - how many stocks to generate
        """
        from time import time
        today = int(time())

        # 2 years ago (epoch seconds)
        SECONDS_PER_DAY = 60 * 60 * 24
        DAY1 = today - SECONDS_PER_DAY * 356 * 2
        STOCK_NUM = 20
        FUNDS_NUM = 10

        URL = 'http://finance.yahoo.com/'

        @classmethod
        def gen_symbol(cls, length):
            """
            generate a len letter symbol
            """

            def c():
                return chr(random.randint(ord('A'), ord('Z')))

            s = ''
            for i in range(length):
                s += c()
            return s

        @classmethod
        def gen_date(cls):
            """
            generate a date between 2014-1-1 to today
            """
            return random.randint(Dao.FakeDao.DAY1, Dao.FakeDao.today)

        @classmethod
        def gen_dates(cls):
            """
            :return: a sequence of the epoch representation of each day from DAY1 to today
            """
            return range(Dao.FakeDao.DAY1, Dao.FakeDao.today + Dao.FakeDao.SECONDS_PER_DAY, Dao.FakeDao.SECONDS_PER_DAY)

        @classmethod
        def gen_expense_ratio(cls):
            return random.uniform(0.1, 3)

        @classmethod
        def gen_price(cls, min_price, max_price):
            return random.uniform(min_price, max_price)

        @classmethod
        def gen_allocation(cls, parties):
            allocations = {}
            remain = 100
            id = 1
            while True:
                if len(allocations) == parties - 1:
                    # the last one
                    allocations[id] = remain
                    break
                else:
                    allocations[id] = random.uniform(1, remain - 1)
                    remain -= allocations[id]
                id += 1
            return allocations

        def __init__(self):
            # create the DB in memory and then populate random generated data
            super().__init__(":memory:")
            super().connect()
            # run the SQL script
            self.conn.executescript(get_sql_scripts())

            # read back meta data
            instrument_type = {x['type']: x['ROWID'] for x in self.exec('SELECT ROWID,type FROM instrument_type')}
            currencies = {x['name']: x['ROWID'] for x in self.exec('SELECT ROWID,name FROM currency')}

            # randomly generate instruments
            self.gen_instruments("XYZ", currencies["USD"], (instrument_type["Stock"], instrument_type["ETF"]), 3,
                                 Dao.FakeDao.STOCK_NUM)
            self.gen_instruments("ABC", currencies["JPY"], (instrument_type["Funds"],), 5, Dao.FakeDao.FUNDS_NUM)

            # what stocks/ETFs we have generated ?
            stocks = [x['ROWID'] for x in self.exec('SELECT ROWID FROM instrument WHERE type = ? OR type = ?',
                                                    (instrument_type["Stock"], instrument_type["ETF"]))]

            # randomly generate stock quotes - from DAY1 to today
            quotes = []
            for day in Dao.FakeDao.gen_dates():
                for i in stocks:
                    min_price = random.randint(5, 100)
                    max_price = 2 * min_price
                    # instrument id, price, date
                    quotes.append((i, Dao.FakeDao.gen_price(min_price, max_price), day))
            self.exec_many('INSERT INTO quote VALUES (?,?,?)', quotes)

            # randomly generate USD => JPY exchange rates - from DAY1 to today
            xccy = []
            for day in Dao.FakeDao.gen_dates():
                # from , to, rate, date
                xccy.append((currencies["USD"], currencies["JPY"], Dao.FakeDao.gen_price(100, 120), day))
            self.exec_many('INSERT INTO xccy VALUES (?,?,?,?)', xccy)

            # buy >1000 shares for each stock/ETF at random price on DAY1
            buy = []
            for i in stocks:
                # instrument id, BUY, price, shares, fee, date
                buy.append((i, 'BUY', Dao.FakeDao.gen_price(20, 1000), random.randint(1000, 2000),
                            Dao.FakeDao.gen_price(5, 20), Dao.FakeDao.DAY1))
            self.exec_many('INSERT INTO [transaction] VALUES (?,?,?,?,?,?)', buy)

            # sell < 400 twice for each one we bought on random day after day one
            sell = []
            for x in range(2):
                for i in stocks:
                    # instrument id, SELL, price, shares, fee, date
                    sell.append((i, 'SELL', Dao.FakeDao.gen_price(20, 1000), random.randint(100, 400),
                                 Dao.FakeDao.gen_price(5, 20), Dao.FakeDao.gen_date()))
            self.exec_many('INSERT INTO [transaction] VALUES (?,?,?,?,?,?)', sell)

            # randomly generate mutual funds performance

        def connect(self):
            pass

        def close(self):
            pass

        def gen_instruments(self, broker, currency, instrument_types, symbol_len, count):
            """
            randomly generate instruments
            :return: None
            """
            # read meta data
            brokers = {x['name']: x['ROWID'] for x in self.exec('SELECT ROWID,name FROM broker')}

            instruments = set()
            while len(instruments) < count:
                symbol = Dao.FakeDao.gen_symbol(symbol_len)
                if symbol in instruments:
                    continue

                instruments.add(symbol)
                # name, instrument type, broker, currency, url, expense ratio
                self.exec('INSERT INTO instrument VALUES (?,?,?,?,?,?)',
                          (symbol,
                           random.choice(instrument_types),
                           brokers[broker],
                           currency,
                           Dao.FakeDao.URL,
                           Dao.FakeDao.gen_expense_ratio()
                           ))
                # get instrument id
                instrument_id = self.exec('SELECT rowid FROM instrument WHERE name=?', (symbol,))[0]['ROWID']

                # asset allocation
                for k, v in Dao.FakeDao.gen_allocation(7).items():
                    # instrument id, asset id, ratio
                    self.exec('INSERT INTO asset_allocation VALUES (?,?,?)',
                              (instrument_id, k, v))

                # region allocation
                for k, v in Dao.FakeDao.gen_allocation(7).items():
                    # instrument id, region id, ratio
                    self.exec('INSERT INTO region_allocation VALUES (?,?,?)',
                              (instrument_id, k, v))

    singleton = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not Dao.singleton:
            if len(args) == 1 or args[1] is None:
                Dao.singleton = Dao.FakeDao()
            else:
                Dao.singleton = Dao.RealDao(args[1])
        return Dao.singleton

    def __getattr__(self, item):
        return getattr(self.singleton, item)

    def __setattr__(self, key, value):
        return setattr(self.singleton, key, value)

if __name__ == "__main__":
    d = Dao(None)
    d.connect()
    d.exec_many("INSERT INTO region VALUES (?)", [("US",), ("Europe",), ("Japan",), ("Emerge",)])
    d.close()

    for f in d.exec("SELECT ROWID,name FROM region"):
        print("%d\t%s" % (f["ROWID"], f["name"]))
