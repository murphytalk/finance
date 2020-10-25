#!/usr/bin/env python
"""
Usage:
    strategy.py avg -d=<days> <ticker>...
    strategy.py -h | --help

Options:
    -h, --help        Show this screen
    -d=<days>         back days
"""
from yahoo_historical import Fetcher
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class AvgClosing:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.data = None
        self.load_data(start_date,  end_date)

    def get_last_date_in_data(self):
        return self.data['Date'].tail(1).item()

    def load_data(self, start_date, end_date):
        ticker = self.ticker
        if self.data is None:
            d1 = [start_date.year, start_date.month, start_date.day]
            d2 = [end_date.year, end_date.month, end_date.day]
            self.data = Fetcher(ticker, d1, d2).get_historical()
        else:
            last = datetime.strptime(self.get_last_date_in_data(), '%Y-%m-%d')
            start_date = last + timedelta(days=1)
            if start_date <= end_date:
                d1 = [start_date.year, start_date.month, start_date.day]
                d2 = [end_date.year, end_date.month, end_date.day]
                extra = Fetcher(ticker, d1, d2).get_historical()
                self.data = self.data.append(extra)

    def calc_avg(self, back_days):
        hist = self.data.tail(back_days)
        # display(hist)
        closings = hist['Close']
        t_1_closing = closings[-1:]
        avg = closings.mean()
        return (t_1_closing - avg) / avg

class AvgClosingWithPreLoadedData(AvgClosing):
    def __init__(self, ticker, preload_data, start_date, end_date):
        pass

    def load_data(self, start_date, end_date):
        pass

    def calc_avg(self, back_days):
        

class Side(Enum):
    BUY = 1
    SELL = 2


@dataclass
class Action:
    side: Side
    # BUY : percentage of normal buy volume
    # SELL: percentage of total position
    percentage: float


if __name__ == "__main__":
    from docopt import docopt

    args = docopt(__doc__)
    # print(args)

    if args['avg']:
        days = int(args['-d'])

        d1 = datetime(2020, 1, 1)
        d2 = datetime(2020, 2, 1)

        avg = AvgClosing('VT', d1, d2)
        print(avg.calc_avg(days))

        avg.load_data(d1, datetime(2020, 2, 10))
        print(avg.calc_avg(days))
