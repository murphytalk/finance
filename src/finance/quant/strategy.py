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
from datetime import timedelta
from dataclasses import dataclass
from enum import Enum


def format_date(dt):
    return dt.strftime("%Y-%m-%d")


@dataclass
class Avg:
    avg_closing: float
    last_to_avg_percentage: float


def do_calc_avg(hist_data):
    closings = hist_data['Close']
    t_1_closing = closings[-1:].iat[0]
    avg = closings.mean()
    return Avg(avg, (t_1_closing - avg) / avg)


def calc_avg(ticker, t_minus_1, back_days):
    start_date = t_minus_1 - timedelta(days=back_days)
    end_date = t_minus_1 + timedelta(days=1)
    d1 = [start_date.year, start_date.month, start_date.day]
    d2 = [end_date.year, end_date.month, end_date.day]
    data = Fetcher(ticker, d1, d2).get_historical()
    return do_calc_avg(ticker, data)


def calc_avg_with_preloaded_data(preloaded_data, t_minus_1, back_days):
    def get_idx_by_date(dt):
        while(True):
            df = preloaded_data[preloaded_data['Date'] == format_date(dt)]
            # print(format_date(dt),df)
            if df.empty:
                dt = dt - timedelta(days=1)
            else:
                # print("idx=",df.index[0])
                return df.index[0]

    start_date = t_minus_1 - timedelta(days=back_days)
    end_date = t_minus_1
    data = preloaded_data.iloc[get_idx_by_date(start_date):get_idx_by_date(end_date)+1]
    return do_calc_avg(data)


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
