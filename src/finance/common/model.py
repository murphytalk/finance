# -*- coding: utf-8 -*-
from collections import deque
from functools import reduce
from json import dumps
from typing import Deque
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

        def __eq__(self, other):
            if isinstance(other, Position.Unclosed):
                return self.price == other.price and self.shares == other.shares and self.fee == other.fee
            return False

        def __repr__(self):
            return f"Unclosed position, price={self.price}, shares={self.shares}, fee={self.fee}"

    def __init__(self, instrument, name, *shares_liq_fee_unclosed):
        self.instrument: int = instrument
        self.name: str = name

        if (len(shares_liq_fee_unclosed) == 0):
            self.shares: float = 0.0  # current shares
            self.liquidated: float = 0.0  # negative value => money(original value) still in market
            self.fee: float = 0.0
            self.unclosed_positions: Deque() = deque()
        else:
            # only for unit tests
            self.shares = shares_liq_fee_unclosed[0]
            self.liquidated = shares_liq_fee_unclosed[1]
            self.fee = shares_liq_fee_unclosed[2]
            self.unclosed_positions = shares_liq_fee_unclosed[3]

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.instrument == other.instrument and self.name == other.name and self.shares == other.shares and self.liquidated == other.liquidated and self.fee == other.fee and self.unclosed_positions == other.unclosed_positions
        return False

    def transaction(self, trans_type: str, price: float, shares: float, fee: float):
        if trans_type == 'SPLIT':
            # 1 to N share split, here price is the N
            self.shares = self.shares * price

            # apply to all unclosed positions
            for c in self.unclosed_positions:
                c.split(price)
        else:
            s = shares if trans_type == 'BUY' else (-1 if shares > 0 else 1) * shares
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
                        shares = 0
                    elif self.unclosed_positions[0].shares == shares:
                        self.unclosed_positions.popleft()
                        shares = 0
                    else:
                        shares -= self.unclosed_positions[0].shares
                        self.unclosed_positions.popleft()

    def VWAP(self):
        calc_vwap = reduce(
            lambda x, y: Position.Unclosed(x.price + y.price * y.shares, x.shares + y.shares, x.fee + y.fee),
            self.unclosed_positions, Position.Unclosed(0, 0, 0))
        return 0 if calc_vwap.shares == 0 else (calc_vwap.price + calc_vwap.fee) / calc_vwap.shares

    def __repr__(self):
        return f"Name={self.name},Shares={self.shares},Fee={self.fee},Liquidated={self.liquidated}, unclosed pos={self.unclosed_positions}"


class Quote(Model):
    def __init__(self, instrument, name, price, quote_date):
        self.instrument = instrument
        self.symbol = name
        self.price = price
        self.date = epoch2date(quote_date)  # the actual date

    def __repr__(self):
        return "Date={},symbol={},id={},price={}".format(self.date, self.symbol, self.instrument, self.price)


class InstrumentType(Model):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
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

    def __repr__(self):
        return u"id={},type={}".format(self.id, self.instrument_type)
