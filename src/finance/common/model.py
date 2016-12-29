# -*- coding: utf-8 -*-
from json import dumps
from finance.common.utils import epoch2date


class Model:
    def __init__(self):
        pass

    def to_json(self):
        return dumps(self.__dict__)


class Position(Model):
    def __init__(self, instrument, name):
        self.instrument = instrument
        self.name = name
        self.shares = 0
        self.liquidated = 0  # negative value => money(original value) still in market
        self.fee = 0

    def transaction(self, trans_type, price, shares, fee):
        if trans_type == 'SPLIT':
            # 1 to N share split, here price is the N
            self.shares = self.shares * price
        else:
            s = shares if trans_type == 'BUY' else -1 * shares
            self.shares = self.shares + s
            self.liquidated -= price * s
            self.fee = self.fee + fee

    def __str__(self):
        return "Name=%4s,Shares=%4d,Fee=%6.2f,Liquidated=%10.2f" % (self.name, self.shares, self.fee, self.liquidated)


class Quote(Model):
    def __init__(self, instrument, name, price, quote_date):
        self.instrument = instrument
        self.symbol = name
        self.price = price
        self.date = epoch2date(quote_date)  # the actual date

    def __str__(self):
        return "Date={},symbol={},id={},price={}".format(self.date, self.symbol, self.instrument, self.price)


class InstrumentType(Model):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return "id={},name={}".format(self.id, self.name)


class Instrument(Model):
    def __init__(self, instrument_id, name, instrument_type, url=None,
                 expense_ratio=None, currency=None, xccy_rate=None, xccy_rate_date=None):
        self.id = instrument_id
        self.name = name
        self.instrument_type = instrument_type
        self.url = url
        self.expense_ratio = expense_ratio
        if currency is not None:
            self.currency = currency
            self.xccy_rate = xccy_rate
            self.xccy_date = epoch2date(xccy_rate_date)

    @classmethod
    def create(cls, instrument_id, name, instrument_type, instrument_type_name,
               url, expense_ratio, currency=None, xccy_rate=None, xccy_rate_date=None):
        return Instrument(instrument_id, name, InstrumentType(instrument_type, instrument_type_name),
                          url, expense_ratio, currency, xccy_rate, xccy_rate_date)

    def __str__(self):
        return "id={},type={}".format(self.id, self.instrument_type)
