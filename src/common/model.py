# -*- coding: utf-8 -*-
from datetime import date
from json import dumps


class Model:
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
            self.liquidated = self.liquidated - price * s
            self.fee = self.fee + fee

    def __str__(self):
        return "Name=%4s,Shares=%4d,Fee=%6.2f,Liquidated=%10.2f" % (self.name, self.shares, self.fee, self.liquidated)


class Quote(Model):
    def __init__(self, instrument, name, price, quote_date):
        self.instrument = instrument
        self.symbol = name
        self.price = price
        self.date = date.fromtimestamp(quote_date)  # the actual date

    def __str__(self):
        return "Date={},symbol={},id={},price={}".format(self.date, self.symbol, self.instrument, self.price)


class InstrumentType(Model):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return "id={},name={}".format(self.id, self.name)


class Instrument(Model):
    def __init__(self, id, name, instrument_type, instrument_type_name, currency, xccy_rate, xccy_rate_date):
        self.id = id
        self.name = name
        self.instrument_type = InstrumentType(instrument_type, instrument_type_name)
        self.currency = currency
        self.xccy_rate = xccy_rate
        self.xccy_date = date.fromtimestamp(xccy_rate_date)
