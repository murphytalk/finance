import random
from json import dumps

from finance.common.dao import ImplDao
from finance.common.dao.db import get_sql_scripts
from finance.common.dao.utils import *
from finance.common.utils import get_valid_db_from_env


class RandomDataDao(ImplDao):
    """
    Using in memory DB with randomly generated market and position data
    """
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

        # populate fake brokers
        self.exec("INSERT INTO broker (name, fullName) VALUES ('ABC', 'ABC Asset Management')")
        self.exec("INSERT INTO broker (name, fullName) VALUES ('XYZ', 'XYZ Securities')")
        self.exec("INSERT INTO broker (name, fullName) VALUES ('IB', 'IB')")

        # read back meta data
        instrument_type = self.get_instrument_types_mapper()
        currencies = self.get_currency_mapper()

        # randomly generate cash positions
        self.exec_many('INSERT INTO cash (ccy,broker,balance) VALUES (?,?,?)',
                       ((currencies['USD'], 1, gen_price(10000, 20000)),
                        (currencies['USD'], 2, gen_price(20000, 30000)),
                        (currencies['CNY'], 1, gen_price(50000, 80000)),
                        (currencies['JPY'], 1, gen_price(1000000, 2000000))))

        # randomly generate instruments
        self.gen_instruments("XYZ", currencies["USD"], (instrument_type["Stock"], instrument_type["ETF"]), 3,
                             STOCK_NUM)
        self.gen_instruments("ABC", currencies["JPY"], (instrument_type["Funds"],), 5, FUNDS_NUM)

        # what stocks/ETFs we have generated ?
        stocks = [x['id'] for x in self.exec('SELECT id FROM instrument WHERE type = ? OR type = ?',
                                                (instrument_type["Stock"], instrument_type["ETF"]))]
        # what funds we have generated ?
        funds = [x['id'] for x in self.exec('SELECT id FROM instrument WHERE type = ?',
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
        for day in gen_dates():
            for i in stocks:
                min_price = random.randint(5, 100)
                max_price = 2 * min_price
                # instrument id, price, date
                quotes.append((i, gen_price(min_price, max_price), day))
        self.exec_many('INSERT INTO quote VALUES (?,?,?)', quotes)

        # randomly generate USD => JPY and CNY=>JPY exchange rates - from DAY1 to today
        xccy = []
        for day in gen_dates():
            # from , to, rate, date
            xccy.append((currencies["USD"], currencies["JPY"], gen_price(100, 120), day))
            xccy.append((currencies["CNY"], currencies["JPY"], gen_price(13, 20), day))
        self.exec_many('INSERT INTO xccy VALUES (?,?,?,?)', xccy)

        # buy >1000 shares for each stock/ETF at random price on DAY1
        buy = []
        for i in stocks:
            # instrument id, BUY, price, shares, fee, date
            buy.append((i, 'BUY', gen_price(20, 1000), random.randint(1000, 2000),
                        gen_price(5, 20), DAY1))
        self.exec_many('INSERT INTO [transaction] VALUES (?,?,?,?,?,?)', buy)

        # sell < 400 twice for each one we bought on random day after day one
        sell = []
        for x in range(2):
            for i in stocks:
                # instrument id, SELL, price, shares, fee, date
                sell.append((i, 'SELL', gen_price(20, 1000), random.randint(100, 400),
                             gen_price(5, 20), gen_date()))
        self.exec_many('INSERT INTO [transaction] VALUES (?,?,?,?,?,?)', sell)

        # randomly generate mutual funds performance
        performance = []
        for day in gen_dates():
            for i in funds:
                # instrument id, amount, price, value, profit, capital date
                amount = random.randint(100, 1000)
                price = gen_price(1000, 10000)
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
        brokers = {x['name']: x['id'] for x in self.exec('SELECT id,name FROM broker')}

        instruments = set()
        while len(instruments) < count:
            symbol = gen_symbol(symbol_len)
            if symbol in instruments:
                continue

            instruments.add(symbol)
            # name, instrument type, broker, currency, url, expense ratio
            self.exec('INSERT INTO instrument ( name , type , broker , currency , "url" , "expense_ratio") VALUES (?,?,?,?,?,?)',
                      (symbol,
                       random.choice(instrument_types),
                       brokers[broker],
                       currency,
                       URL,
                       gen_expense_ratio()
                       ))
            # get instrument id
            instrument_id = self.exec('SELECT id FROM instrument WHERE name=?', (symbol,))[0]['id']

            # asset allocation
            for k, v in gen_allocation(7).items():
                # instrument id, asset id, ratio
                self.exec('INSERT INTO asset_allocation VALUES (?,?,?)',
                          (instrument_id, k, v))

            # country allocation
            for k, v in gen_allocation(11).items():
                # instrument id, country id, ratio
                self.exec('INSERT INTO country_allocation VALUES (?,?,?)',
                          (instrument_id, k, v))