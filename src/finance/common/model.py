# -*- coding: utf-8 -*-
from collections import deque
from functools import reduce
from json import dumps

from finance.common.utils import epoch2date


class Model:
    def __init__(self):
        pass

    def to_json(self):
        return dumps(self.__dict__)


class Position(Model):
    class Unclosed:
        # data class will be introduced in 3.7
        def __init__(self, price, shares, fee):
            self.price = price
            self.shares = shares
            self.fee = fee

        def split(self, factor):
            self.price = self.price / factor
            self.shares = self.shares * factor

        def __str__(self):
            return "Unclosed position, price=%f, shares=%d, fee=%f" % (self.price, self.shares, self.fee)

    def __init__(self, instrument, name):
        self.instrument = instrument
        self.name = name
        self.shares = 0  # current shares
        self.liquidated = 0  # negative value => money(original value) still in market
        self.fee = 0
        self.unclosed_positions = deque()

    def transaction(self, trans_type, price, shares, fee):
        if trans_type == 'SPLIT':
            # 1 to N share split, here price is the N
            self.shares = self.shares * price

            # apply to all unclosed positions
            for c in self.unclosed_positions:
                c.split(price)
        else:
            s = shares if trans_type == 'BUY' else -1 * shares
            self.shares = self.shares + s
            self.liquidated -= price * s
            self.fee = self.fee + fee

            if s > 0:
                # buy
                self.unclosed_positions.append(Position.Unclosed(price, shares, fee))
            else:
                # sell
                while shares > 0:
                    if len(self.unclosed_positions) == 0:
                        raise RuntimeError("Not enough unclosed position")
                    if self.unclosed_positions[0].shares > shares:
                        self.unclosed_positions[0].shares -= shares
                    elif self.unclosed_positions[0].shares == shares:
                        self.unclosed_positions.popleft()
                    else:
                        shares -= self.unclosed_positions[0].shares
                        self.unclosed_positions.popleft()

    def VWAP(self):
        calc_vwap = reduce(
            lambda x, y: Position.Unclosed(x.price * x.share + y.price * y.share, x.share + y.share, x.fee + y.fee),
            self.unclosed_positions, Position.Unclosed(0, 0, 0))
        return (calc_vwap.price + calc_vwap.fee) / calc_vwap.shares

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
