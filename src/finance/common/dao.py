# -*- coding: utf-8 -*-
import random
import sqlite3
from json import dumps
from calendar import timegm
from finance.common.utils import date_str2epoch, get_current_date_epoch, SECONDS_PER_DAY
from finance.common.db import get_sql_scripts
from finance.common.model import *
from finance.common.utils import get_valid_db_from_env

import logging.config

log = logging.getLogger(__name__)


# import traceback
# def g():
#    for line in traceback.format_stack():
#        print(line.strip())

def _remove_empty_value(func):
    def wrapper(s, name, data):
        to_be_del = []
        for k, v in data.items():
            if (type(v) is int) or (type(v) is float):
                if v == 0:
                    to_be_del.append(k)
            elif type(v) is str:
                if len(v) == 0:
                    to_be_del.append(k)
        for k in to_be_del:
            data.pop(k, None)

        return func(s, name, data)

    return wrapper


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
            self.conn.commit()
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
              type id
              type name
              url
              expense ration
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

        def get_stock_latest_quotes(self, quote_date):
            """
            get the latest quotes of all stocks before the given date
            :param quote_date: quote date
            :return: dict {instrument id : Quote}
            """
            quotes = {}
            for i, n in [(r['ROWID'], r['name']) for r in self.exec('SELECT ROWID, name from instrument')]:
                for r in self.exec('SELECT  price, date FROM quote WHERE instrument = ? ORDER BY date DESC LIMIT 1',
                                   (i,)):
                    quotes[i] = Quote(i, n, r['price'], r['date'])

            return quotes

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
                   'LEFT JOIN ( SELECT * FROM xccy_hist WHERE date =(SELECT max(date) FROM xccy_hist WHERE date<=?)) x '
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
                yield r

        def _get_instrument_id(self, **kwargs):
            instrument_id = kwargs['instrument_id'] if 'instrument_id' in kwargs else None
            if instrument_id is None:
                for r in self.exec('SELECT ROWID FROM instrument WHERE name=?', (kwargs['instrument_name'],)):
                    instrument_id = r['ROWID']
                    break
            return instrument_id

        def get_asset_allocation(self, **kwargs):
            """
            get asset allocation of the given instrument
            :param kwargs:  instrument_id or instrument_name
            :return: a generator of (asset,ratio)
            """
            instrument_id = self._get_instrument_id(**kwargs)
            if instrument_id:
                sql = ('SELECT t.type,a.ratio FROM asset_allocation a, asset t WHERE a.instrument = ? '
                       'AND a.asset=t.rowid ORDER BY a.asset')
                for r in self.exec(sql, (int(instrument_id),)):
                    yield (r['type'], r['ratio'])

        def get_country_allocation(self, **kwargs):
            """
            get country allocation of the given instrument
            :param kwargs:  instrument_id or instrument_name
            :return: a generator of (country,ratio)
            """
            instrument_id = self._get_instrument_id(**kwargs)
            if instrument_id:
                sql = ('SELECT t.name,a.ratio FROM country_allocation a, country t WHERE a.instrument = ? '
                       'AND a.country=t.rowid ORDER BY a.country')
                for r in self.exec(sql, (int(instrument_id),)):
                    yield (r['name'], r['ratio'])

        def get_region_allocation(self, **kwargs):
            """
            get region allocation of the given instrument
            :param kwargs:  instrument_id or instrument_name
            :return: a generator of (country,ratio)
            """
            instrument_id = self._get_instrument_id(**kwargs)
            if instrument_id:
                # get country id => region def
                sql = ('SELECT r.name region, rs.country FROM regions rs '
                       'JOIN region r ON rs.region = r.ROWID JOIN country c ON rs.country = c.ROWID')
                region_lookup = {r['country']: r['region'] for r in self.exec(sql)}

                sql = ('SELECT t.ROWID as cid, a.ratio FROM country_allocation a, country t '
                       'WHERE a.instrument = ? AND a.country=t.rowid')

                regions = {}
                for r in self.exec(sql, (int(instrument_id),)):
                    country = r['cid']
                    region = region_lookup[country]
                    if region in regions:
                        regions[region] += r['ratio']
                    else:
                        regions[region] = r['ratio']

                for region, ratio in regions.items():
                    yield (region, ratio)

        def get_asset_types(self):
            for r in self.exec('SELECT ROWID, type FROM asset'):
                yield (r['ROWID'], r['type'])

        def get_countries(self):
            for r in self.exec('SELECT ROWID, [name] FROM country'):
                yield (r['ROWID'], r['name'])

        def get_brokers(self):
            for r in self.exec('SELECT ROWID, [name],fullName FROM broker'):
                yield (r['ROWID'], r['name'], r['fullName'])

        def get_instrument_types(self):
            for r in self.exec('SELECT ROWID, type FROM instrument_type'):
                yield (r['ROWID'], r['type'])

        def _update_instrument_allocations(self, instrument_name, payload, allocation_name, allocation_col_name):
            kwargs = {'instrument_name': instrument_name}
            instrument_id = self._get_instrument_id(**kwargs)
            if instrument_id:
                types = {x[allocation_col_name]: x['ROWID'] for x in
                         self.exec('SELECT ROWID,%s FROM %s' % (allocation_col_name, allocation_name))}
                sum_alloc = 0
                allocations = []
                self.exec('DELETE from %s_allocation WHERE instrument = ?' % allocation_name, (instrument_id,))
                for x in payload:
                    allocations.append((instrument_id, types[x[allocation_name]], x['ratio']))
                    sum_alloc += x['ratio']
                if sum_alloc < 100:
                    allocations.append((instrument_id, types['Other'], 100 - sum_alloc))

                self.exec_many('INSERT INTO %s_allocation VALUES (?,?,?)' % allocation_name, allocations)

                return True
            else:
                return False

        def update_instrument_asset_allocations(self, instrument_name, assets):
            """
            Update instrument asset allocations
            :param instrument_name:  name (not ID) of an instrument
            :param assets: a dict of the asset allocation.
                   See POST API:  /instrument/allocation/asset/{instrument}
            :return: True/False
            """
            return self._update_instrument_allocations(instrument_name, assets['assets'], 'asset', 'type')

        def update_instrument_country_allocations(self, instrument_name, countries):
            """
            Update instrument country allocations
            :param instrument_name:  name (not ID) of an instrument
            :param countries: a dict of the country allocation.
                   See POST API: /instrument/allocation/country/{instrument}
            :return: True/False
            """
            return self._update_instrument_allocations(instrument_name, countries['countries'], 'country', 'name')

        def get_instruments(self, instrument_name=None):
            sql = ('SELECT i.ROWID, i.name, t.type, c.name AS currency, b.name AS broker, i.url, i.expense_ratio '
                   'FROM instrument i '
                   'JOIN instrument_type t ON i.type = t.ROWID '
                   'JOIN currency c ON i.currency = c.ROWID '
                   'JOIN broker b ON i.broker = b.ROWID')
            if instrument_name:
                sql += ' WHERE i.name = ?'
            for r in self.exec(sql, (instrument_name,) if instrument_name else None):
                yield {'id': r['ROWID'],
                       'name': r['name'],
                       'type': r['type'],
                       'currency': r['currency'],
                       'broker': r['broker'],
                       'url': r['url'],
                       'expense': r['expense_ratio']}

        def get_instrument_types_mapper(self):
            return {x[1]: x[0] for x in self.get_instrument_types()}

        def get_currency_mapper(self):
            return {x['name']: x['ROWID'] for x in self.exec('SELECT ROWID,[name] FROM currency')}

        def get_broker_mapper(self):
            return {x['name']: x['ROWID'] for x in self.exec('SELECT ROWID,[name] FROM broker')}

        @_remove_empty_value
        def update_instrument(self, instrument_name, instrument):
            """
            Update/Insert an instrument
            :param instrument_name: Instrument name
            :param instrument: a dict which holds detailed instrument information
                   see POST API /instrument/{instrument}
            :return: True/False
            """
            kwargs = {'instrument_name': instrument_name}
            instrument_id = self._get_instrument_id(**kwargs)

            types = self.get_instrument_types_mapper()
            brokers = self.get_broker_mapper()
            ccy = self.get_currency_mapper()

            params = []
            cols = []

            if 'type' in instrument:
                cols.append('type')
                params.append(types[instrument['type']])
            if 'broker' in instrument:
                cols.append('broker')
                params.append(brokers[instrument['broker']])
            if 'currency' in instrument:
                cols.append('currency')
                params.append(ccy[instrument['currency']])
            if 'url' in instrument:
                cols.append('url')
                params.append(instrument['url'])
            if 'expense' in instrument:
                cols.append('expense_ratio')
                params.append(instrument['expense'])

            if instrument_id:
                sql = 'UPDATE instrument set '
                sql += ','.join([x + '=?' for x in cols]) + ' WHERE ROWID = ?'
                params.append(instrument_id)
            else:
                sql = 'INSERT INTO instrument ('
                sql += ','.join(cols) + ',name) VALUES (' + ','.join(['?' for x in params]) + ',?)'
                params.append(instrument_name)

            # log.info('update instrument %s,SQL = %s, params=%s ', instrument_name, sql, params)
            self.exec(sql, tuple(params))

            return True

        def get_stock_transaction(self, stock_name=None):
            sql = 'SELECT date,name,type,price,shares,fee FROM stock_trans '
            if stock_name is not None:
                sql += 'WHERE name = ?'
            for x in self.exec(sql, (stock_name,) if stock_name else None):
                yield {
                    'date': str(epoch2date(x['date'])),
                    'symbol': x['name'],
                    'type': x['type'],
                    'price': x['price'],
                    'shares': x['shares'],
                    'fee': x['fee']}

        @_remove_empty_value
        def update_stock_transaction(self, stock_name, transaction):
            """
            Update/Insert a stock transaction.
            :param stock_name: Stock name
            :param transaction: A dict that holds transaction details
                   see POST API /transaction/stock/{stock}
            :return: True/False
            """
            kwargs = {'instrument_name': stock_name}
            instrument_id = self._get_instrument_id(**kwargs)
            if instrument_id > 0:
                self.exec('INSERT INTO [transaction] (instrument, type, price, shares, fee, date) '
                          'VALUES (?,?,?,?,?,?)',
                          (instrument_id,
                           transaction['Type'],
                           transaction['Price'],
                           transaction['Shares'],
                           transaction['Fee'],
                           date_str2epoch(transaction['Date'])))
                return True
            else:
                return False

        @_remove_empty_value
        def update_stock_quotes(self, stock_name, quotes):
            """
            Update/Insert stock quote for one day
            :param stock_name: stock name
            :param quotes: [{Date,Price},]
            :return: True/False
            """
            kwargs = {'instrument_name': stock_name}
            instrument_id = self._get_instrument_id(**kwargs)
            if instrument_id > 0:
                parameters = [(instrument_id, date_str2epoch(q['Date']), q['Price']) for q in quotes['quotes']]
                # remove existing quotes if there is any
                self.exec_many('DELETE FROM quote WHERE instrument = ? and date = ?', [p[:2] for p in parameters])
                # then insert
                self.exec_many('INSERT INTO quote (instrument, date, price) '
                               'VALUES (?,?,?)', parameters)
                return True
            else:
                return False

        def get_xccy_quote(self, ccy_pair=None, max_days=None):
            """
            Get xccy quotes
            :param ccy_pair: if specified then return only quotes of the specified currency pair
            :param max_days: if specified then only return quotes of the last days from today
            :return: a generator of Date/From/To/Rate dict
            """
            params = []
            sql = 'SELECT [From],[To],rate,date FROM xccy_hist '
            if ccy_pair is not None:
                sql += 'WHERE [From]=? and [To]=? '
                params.append(ccy_pair[0])
                params.append(ccy_pair[1])
            if max_days is not None:
                no_earlier_than = get_current_date_epoch() - max_days * SECONDS_PER_DAY
                sql += ' %s date >= ? ' % ('AND' if ccy_pair is not None else 'WHERE')
                params.append(no_earlier_than)

            sql += 'ORDER BY date DESC'
            for x in self.exec(sql, tuple(params) if len(params) > 0 else None):
                yield {'Date': str(epoch2date(x['date'])),
                       'From': x['From'],
                       'To': x['To'],
                       'Rate': x['rate']}

        def get_stock_quote(self, stock_name=None, max_days=None):
            """
            Get stock quotes
            :param stock_name: if specified then return only quotes of this stock
            :param max_days: if specified then only return quotes of the last days from today
            :return: a generator of date/symbol/price dict
            """
            params = []
            latest = 0
            # find latest quote date first
            sql = 'SELECT max(date) as lt FROM stock_quote '
            if stock_name is not None:
                sql += 'WHERE name = ? '
                params.append(stock_name)
            for r in self.exec(sql, params):
                latest = r['lt']

            if latest is None:
                latest = 0

            params = []

            sql = 'SELECT * FROM stock_quote '
            if stock_name is not None:
                sql += 'WHERE name = ? '
                params.append(stock_name)
            if max_days is not None:
                no_earlier_than = latest - max_days * SECONDS_PER_DAY
                sql += ' %s date >= ? ' % ('AND' if stock_name is not None else 'WHERE')
                params.append(no_earlier_than)

            sql += 'ORDER BY date DESC'
            for x in self.exec(sql, params if len(params) > 0 else None):
                yield {'date': str(epoch2date(x['date'])), 'symbol': x['name'], 'price': x['price']}

        def get_filter_names(self):
            return [x['name'] for x in self.exec('SELECT name FROM filter')]

        def get_filters(self, name=None):
            filters = {}

            sql = 'SELECT * from instrument_filters '
            if name is None:
                param = None
            else:
                sql += 'WHERE filter_name=?'
                param = (name,)

            for x in self.exec(sql, param):
                f = {'id': x['instrument_id'], 'name': x['instrument_name']}
                if x['filter_name'] in filters:
                    filters[x['filter_name']]['instruments'].append(f)
                else:
                    filters[x['filter_name']] = {'extra': x['extra'], 'instruments': [f] if f['id'] else None}
            return filters

        @_remove_empty_value
        def update_filter(self, name, filters):
            def _get_id():
                for r in self.exec('SELECT ROWID FROM instrument_filter_name WHERE name=?', [name, ]):
                    return r['ROWID']
                return None

            filter_id = _get_id()
            if filter_id is None:
                self.exec('INSERT INTO instrument_filter_name VALUES (?,?)', (name, filters['extra']))
                filter_id = _get_id()
            else:
                self.exec('UPDATE instrument_filter_name SET extra = ? WHERE ROWID = ?', (filters['extra'], filter_id))

            self.exec('DELETE FROM filter WHERE filter = ?', [filter_id, ])

            all_instruments = {x['name']: x['ROWID'] for x in self.exec('SELECT ROWID,name FROM instrument')}
            params = [(filter_id, all_instruments[i['name']]) for i in filters['instruments']]
            self.exec_many('INSERT INTO filter VALUES (?,?)', params)

        def get_all_positions(self):
            pass

    class FakeDao(RealDao):
        """
        Using in memory DB with randomly generated market and position data
        """
        from time import time
        today = int(time())

        SECONDS_PER_DAY = 60 * 60 * 24
        # 2 years ago (epoch seconds)
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
            super().__init__(get_valid_db_from_env('FAKE_DB', ":memory:"))
            super().connect()

            # check if tables already created
            c = 0
            row = self.exec("SELECT count(*) as C FROM sqlite_master WHERE type='table' AND name='asset'")
            for r in row:
                c = r['C']
                break
            if c == 1:
                return

            # run the SQL script to generate tables and views, then populate meta data
            self.conn.executescript(get_sql_scripts())

            # read back meta data
            instrument_type = self.get_instrument_types_mapper()
            currencies = self.get_currency_mapper()

            # randomly generate instruments
            self.gen_instruments("XYZ", currencies["USD"], (instrument_type["Stock"], instrument_type["ETF"]), 3,
                                 Dao.FakeDao.STOCK_NUM)
            self.gen_instruments("ABC", currencies["JPY"], (instrument_type["Funds"],), 5, Dao.FakeDao.FUNDS_NUM)

            # what stocks/ETFs we have generated ?
            stocks = [x['ROWID'] for x in self.exec('SELECT ROWID FROM instrument WHERE type = ? OR type = ?',
                                                    (instrument_type["Stock"], instrument_type["ETF"]))]
            # what funds we have generated ?
            funds = [x['ROWID'] for x in self.exec('SELECT ROWID FROM instrument WHERE type = ?',
                                                   (instrument_type["Funds"],))]
            # populate instrument filters
            self.exec_many('INSERT INTO filter (name) VALUES (?)',
                           [("All-Stocks", ), ("First-Two-Stocks", ), ("All-Funds", )])
            self.exec_many('INSERT INTO instrument_filter VALUES (?,?)',
                           [(1, x) for x in stocks] + [(2, x) for x in stocks[:2]] + [(3, x) for x in funds])

            # one filter with extra logic : reduce the first stock's shares by 100
            for x in self.exec('SELECT name from instrument WHERE ROWID = ?', (stocks[0],)):
                extra = [{'action': 'adjust_shares', 'parameters': {'instrument': x['name'], 'adjustment': -100}}]
                self.exec('INSERT INTO filter (name,extra) VALUES (?,?)', ('First-Stock-Reduce-100-Shares',
                                                                           dumps(extra)))
                break

            # randomly generate stock quotes - from DAY1 to today
            quotes = []
            for day in Dao.FakeDao.gen_dates():
                for i in stocks:
                    min_price = random.randint(5, 100)
                    max_price = 2 * min_price
                    # instrument id, price, date
                    quotes.append((i, Dao.FakeDao.gen_price(min_price, max_price), day))
            self.exec_many('INSERT INTO quote VALUES (?,?,?)', quotes)

            # randomly generate USD => JPY and CNY=>JPY exchange rates - from DAY1 to today
            xccy = []
            for day in Dao.FakeDao.gen_dates():
                # from , to, rate, date
                xccy.append((currencies["USD"], currencies["JPY"], Dao.FakeDao.gen_price(100, 120), day))
                xccy.append((currencies["CNY"], currencies["JPY"], Dao.FakeDao.gen_price(13, 20), day))
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
            performance = []
            for day in Dao.FakeDao.gen_dates():
                for i in funds:
                    # instrument id, amount, price, value, profit, capital date
                    amount = random.randint(100, 1000)
                    price = Dao.FakeDao.gen_price(1000, 10000)
                    value = amount * price
                    profit = value * random.uniform(-1, 2)
                    capital = price - profit
                    performance.append((i, amount, price, value, profit, capital, day))

            self.exec_many('INSERT INTO performance VALUES (?,?,?,?,?,?,?)', performance)

        def connect(self):
            pass

        def close(self):
            self.conn.commit()

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

                # country allocation
                for k, v in Dao.FakeDao.gen_allocation(11).items():
                    # instrument id, country id, ratio
                    self.exec('INSERT INTO country_allocation VALUES (?,?,?)',
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
    d.exec_many("INSERT INTO country VALUES (?)", [("US",), ("Europe",), ("Japan",), ("Emerge",)])
    d.close()

    for f in d.exec("SELECT ROWID,name FROM country"):
        print("%d\t%s" % (f["ROWID"], f["name"]))
