# -*- coding: utf-8 -*-
"""
Various calculations

parameter:
 -fxxxxxxx path to db file
 -i        do not update db file

"""
import sys

from finance.common.const import STOCK_START_DATE
from finance.common.dao import Dao
from finance.common.model import Position
from finance.common.utils import cmdline_args


class CalcPosition:
    def __init__(self, date2):
        self.date1 = STOCK_START_DATE
        self.date2 = date2
        self.positions = None

    def calc(self, d):
        def on_each_transaction(instrument, name, transaction_type, price, shares, fee, the_date):
            pos = self.positions[instrument]
            pos.transaction(transaction_type, price, shares, fee)


        self.positions = d.populate_from_instruments('(i.type = 2 or i.type = 1)',
                                                     lambda instrument_id, name, tid, t, u, e: Position(instrument_id,
                                                                                                        name))
        d.iterate_transaction(self.date1, self.date2, on_each_transaction)


    def dump(self, callback=None):
        for k, v in self.positions.items():
            if callback is None:
                print(k, v)
            else:
                callback(k, v)


if __name__ == '__main__':

    args, others = cmdline_args(sys.argv[1:])
    db = args['dbfile']

    if db is None:
        print('Need a db file')
    else:
        c = CalcPosition(args['end_date'])
        c.calc(db)
        c.dump()
