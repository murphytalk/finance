from calendar import timegm
from finance.common.utils import date_str2epoch, get_current_date_epoch, SECONDS_PER_DAY
from finance.common.model import *
from finance.common.dao.db import Raw

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


class ImplDao(Raw):
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
          row id
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
        return {x['id']: c(x['id'], x['name'], x['type_id'], x['type'], x['url'], x['expense_ratio'])
                for x in self.exec(sql)}

    def get_stock_latest_quotes(self, quote_date):
        """
        get the latest quotes of all stocks before the given date
        :param quote_date: quote date
        :return: dict {instrument id : Quote}
        """
        quotes = {}
        for i, n in [(r['id'], r['name']) for r in self.exec('SELECT id, name from instrument')]:
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
               'FROM fund_performance2')
        for r in self.exec(sql):
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

    def get_country_region_lookup(self):
        # get country id => region def
        sql = ('SELECT r.name region, rs.country FROM regions rs '
                'JOIN region r ON rs.region = r.ROWID JOIN country c ON rs.country = c.ROWID')
        return {r['country']: r['region'] for r in self.exec(sql)}

    def get_region_allocation(self, **kwargs):
        """
        get region allocation of the given instrument
        :param kwargs:  instrument_id or instrument_name
        :return: a generator of (country,ratio)
        """
        instrument_id = self._get_instrument_id(**kwargs)
        if instrument_id:
            region_lookup = self.get_country_region_lookup()

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
            for r in self.exec('SELECT ROWID FROM filter WHERE name=?', [name, ]):
                return r['ROWID']
            return None

        extra = filters['extra'] if 'extra' in filters else None

        filter_id = _get_id()
        if filter_id is None:
            self.exec('INSERT INTO filter VALUES (?,?)', (name, extra))
            filter_id = _get_id()
        else:
            self.exec('UPDATE filter SET extra = ? WHERE ROWID = ?', (extra, filter_id))

        self.exec('DELETE FROM instrument_filter WHERE filter = ?', (filter_id, ))

        all_instruments = {x['name']: x['ROWID'] for x in self.exec('SELECT ROWID,name FROM instrument')}
        params = [(filter_id, all_instruments[i['name']]) for i in filters['instruments']]
        self.exec_many('INSERT INTO instrument_filter VALUES (?,?)', params)

    def get_cash_balance(self):
        for x in self.exec('SELECT * from cash_balance'):
            if x['ccy'] != 'JPY':
                for r in self.exec('SELECT rate from xccy_hist2 WHERE [From] =? ORDER BY datestr DESC LIMIT 1 ',
                                   (x['ccy'],)):
                    rate = r['rate']
                    break
            else:
                rate = 1
            yield x['ccy'], x['broker'], x['balance'], rate

    def update_cash_balance(self, ccy, broker, balance):
        ccy_id = None
        broker_id = None
        for x in self.exec('SELECT ROWID FROM currency WHERE name=?', (ccy,)):
            ccy_id = x['ROWID']
            break
        for x in self.exec('SELECT ROWID FROM broker WHERE name=?', (broker,)):
            broker_id = x['ROWID']
            break
        if ccy_id is None or broker_id is None:
            return False
        else:
            cash_id = None
            for x in self.exec('SELECT ROWID FROM cash WHERE ccy=? and broker=?', (ccy_id, broker_id)):
                cash_id = x['ROWID']
                break
            if cash_id is None:
                sql = 'INSERT INTO cash (balance,ccy,broker) VALUES (?,?,?)'
            else:
                sql = 'UPDATE cash SET balance = ? WHERE ccy=? and broker=?'
            self.exec(sql, (balance['balance'], ccy_id, broker_id))
            return True

