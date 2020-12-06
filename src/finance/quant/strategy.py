#!/usr/bin/env python
"""
Usage:
    strategy.py avg  -d=<days> --up=<up_scale> --down=<down_scale> --invest=<invest> --stop-buy=<stop_buy> --up-scale-limit=<up_limit> <ticker>...
    strategy.py test -d=<days> -f=<date1> -t=<date2> --buy-interval=<days> --invest=<invest> --stop-buy=<stop_buy> --up-scale-limit=<up_limit> <ticker>
    strategy.py -h | --help

Mode:
    avg    compute buy vol by check closing vs last n days avg
    test   Back test

Options:
    -h, --help                   show this screen
    -d=<days>                    back days
    --buy-interval=<days>        days between buying
    --invest=<invest>            base invest amount for each buying
    -f=<date1>                   back test start date in YYYYMMDD format
    -t=<date2>                   back test end date in YYYYMMDD format
    --stop-buy=<stop_buy>        when price is this times of avg stop buying
    --up-scale-limit=<up_limit>  the limit to scale up buy vol
    --up=<up_scale>              up scale
    --down=<down_scale>          down scale
"""
from yahoo_historical import Fetcher
from datetime import timedelta, datetime
from dataclasses import dataclass
from enum import Enum
from math import floor, ceil
from functools import reduce
from numpy import isnan
import concurrent.futures

FMT = "%Y-%m-%d"


def format_date(dt) -> str:
    return dt.strftime(FMT)


def parse_date(dt_str) -> datetime:
    return datetime.strptime(dt_str, FMT)


def format_ratio_to_percent(ratio: float) -> str:
    return '{:.2f}%'.format(ratio*100)


@dataclass
class Avg:
    closing: float
    avg_closing: float
    last_to_avg_percentage: float


def do_calc_avg(hist_data) -> Avg:
    # display(hist_data)
    closings = hist_data['Close']
    t_1_closing = closings[-1:].iat[0]
    avg = closings.mean()
    return Avg(t_1_closing, avg, (t_1_closing - avg) / avg)


def calc_avg(ticker: str, t_minus_1: datetime, back_days: int) -> Avg:
    start_date = t_minus_1 - timedelta(days=back_days)
    end_date = t_minus_1 + timedelta(days=1)
    d1 = [start_date.year, start_date.month, start_date.day]
    d2 = [end_date.year, end_date.month, end_date.day]
    data = Fetcher(ticker, d1, d2).get_historical()
    return do_calc_avg(data)


def ensure_trading_date(preloaded_data, dt: datetime, day_step: int):
    first = parse_date(preloaded_data.iloc[0]['Date'])
    last = parse_date(preloaded_data.tail(1).iloc[0]['Date'])
    # print(first, last)
    while(True):
        if (dt < first or dt > last):
            # print(dt)
            return None
        df = preloaded_data[preloaded_data['Date'] == format_date(dt)]
        # print(format_date(dt),df)
        if df.empty or isnan(df['Close'].iloc[0]):
            dt = dt + timedelta(days=day_step)
        else:
            return df


def calc_avg_with_preloaded_data(preloaded_data, t_minus_1: datetime, back_days: int) -> Avg:
    def get_idx_by_date(dt):
        return ensure_trading_date(preloaded_data, dt, -1).index[0]

    start_date = t_minus_1 - timedelta(days=back_days)
    end_date = t_minus_1
    data = preloaded_data.iloc[get_idx_by_date(
        start_date):get_idx_by_date(end_date)+1]
    return do_calc_avg(data)


class Side(Enum):
    BUY = 1
    SELL = 2


@dataclass
class Action:
    date: datetime
    side: Side
    # BUY : percentage of normal buy volume
    # SELL: percentage of total position
    percentage: float
    explain: str
    avg: Avg
    shares: int = 0


class Strategy:
    def calc(self, date: datetime, avg: Avg) -> Action:
        pass

    def explain_change(self, avg) -> str:
        return '{} {} avg {} by {}'.format(
            avg.closing,
            'above' if avg.last_to_avg_percentage >= 0 else 'below',
            avg.avg_closing,
            format_ratio_to_percent(abs(avg.last_to_avg_percentage))
        )


class FluxtrateBuy(Strategy):
    def __init__(self,
                 scale_up: float,  # how many times of down percentage to increase the buying
                 scale_down: float, stop_buy_level: float, buy_cap: float):
        self.scale_up = scale_up
        self.scale_down = scale_down
        self.stop_buy_level = stop_buy_level
        self.buy_cap = buy_cap

    def calc(self, date: datetime, avg: Avg) -> Action:
        if avg.last_to_avg_percentage >= self.stop_buy_level:
            explain = 'stop buy level {} exceeded, not buying'.format(
                format_ratio_to_percent(self.stop_buy_level))
            return Action(date, Side.BUY, 0, explain, avg)

        if avg.last_to_avg_percentage >= 0:
            v = 1 - self.scale_down * avg.last_to_avg_percentage
            if v < 0:
                v = 0
            explain = self.explain_change(
                avg) + ', scale down buy vol to {}'.format(format_ratio_to_percent(v))
            return Action(date, Side.BUY, v, explain, avg)

        v = 1 - self.scale_up * avg.last_to_avg_percentage
        if v > self.buy_cap:
            v = self.buy_cap
        explain = self.explain_change(
            avg) + ', scale up buy vol to {}'.format(format_ratio_to_percent(v))
        return Action(date, Side.BUY, v, explain, avg)


@dataclass
class EvalResult:
    total_cost: float
    total_value: float
    final_return: float
    annualized_return: float


class BackTester:
    def __init__(self,
                 avg_back_days: int,
                 ticker: str, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date

        self.avg_back_days = avg_back_days
        # buffer for bank holidays
        start_date = start_date - timedelta(days=avg_back_days + 10)
        end_date = end_date + timedelta(days=1)
        d1 = [start_date.year, start_date.month, start_date.day]
        d2 = [end_date.year, end_date.month, end_date.day]
        self.data = Fetcher(ticker, d1, d2).get_historical()

    def get_actions(self, strategy: Strategy, interval_days: int):
        def get_date_from_df(df):
            return parse_date(df['Date'].iat[0])

        actions = []
        dt = self.start_date
        while dt <= self.end_date:
            # get a date when there is valid closing
            dt = get_date_from_df(ensure_trading_date(self.data, dt, 1))
            t_minus_one = dt - timedelta(days=1)
            t_minus_one = get_date_from_df(
                ensure_trading_date(self.data, t_minus_one, -1))
            avg = calc_avg_with_preloaded_data(
                self.data, t_minus_one, self.avg_back_days)
            actions.append(strategy.calc(dt, avg))

            dt += timedelta(days=interval_days)

        return actions

    def evaluate(self, base_invest_vol: float, actions) -> (EvalResult, EvalResult):
        def calc_annualized_return(total_return: float, start_date: datetime, end_date: datetime) -> float:
            days = (end_date - start_date).days
            return total_return / (days / 365)

        def round_shares(shares: float, price_is_up: bool):
            return ceil(shares) if price_is_up else floor(shares)

        @ dataclass
        class Position:
            cost: float
            shares: int

        first_action = actions[0]
        last_action = actions[-1]

        def calc_pos(a: Action, calc_shares) -> Position:
            shares = round_shares(calc_shares(a), a.percentage >= 0)
            cost = shares * a.avg.closing
            return Position(cost, shares)

        my_positions = [calc_pos(
            a, lambda x: base_invest_vol * x.percentage / x.avg.closing) for a in actions]
        standard_positions = [
            calc_pos(a, lambda x: base_invest_vol / x.avg.closing) for a in actions]

        def calc_return(positions) -> EvalResult:
            total_cost = reduce(lambda x, y: x + y.cost,  positions, 0)
            total_shares = reduce(lambda x, y: x + y.shares,  positions, 0)
            total_value = total_shares * last_action.avg.closing
            total_return = (total_value - total_cost) / total_cost
            annualized_return = calc_annualized_return(
                total_return, first_action.date, last_action.date)
            return EvalResult(total_cost, total_value, total_return, annualized_return)

        return (calc_return(my_positions), calc_return(standard_positions))


@dataclass
class Result:
    result: EvalResult
    benchmark: EvalResult
    up_scale: int
    down_scale: int
    actions: list


def calc(up_and_down):
    up, down, stop_buy, buy_cap,t = up_and_down
    s = FluxtrateBuy(up, down, stop_buy, buy_cap)
    actions = t.get_actions(s, 7)
    my, standard = t.evaluate(1000, actions)
    return Result(my, standard, up, down, actions)

def calc_in_parallel(up_down, worker_num):
    with concurrent.futures.ProcessPoolExecutor(max_workers=worker_num) as executor:
        for result in executor.map(calc, up_down):
            yield result


def back_test(back_days, interval, inveset,date1, date2, stop_buy, buy_cap, ticker):
    print(back_days,interval, inveset,date1, date2, stop_buy, buy_cap, ticker)

    t = BackTester(back_days, ticker[0], date1, date2)
    up_down = []
    for up in range(1, 101):
        for down in range(1, 101):
            up_down.append((up/10,down/10,stop_buy, buy_cap,t))


    evaluations = list(calc_in_parallel(up_down, 8))
    evaluations.sort(key=lambda x: x.result.annualized_return)

    worst = evaluations[0]
    best = evaluations[-1]

    def dump(f, caption, result):
        f.write("{}\nup={} down={}\n{}\n".format(caption,result.up_scale, result.down_scale, result.result))
        for a in result.actions:
            f.write("{}\n".format(a))

    with open(ticker[0]+'.txt', 'w+') as f:
        f.write('Benchmark: {}\n'.format(worst.benchmark))
        dump(f,'Best', best)
        dump(f,'Worst', worst)


def parse_datetime(ymd):
    return datetime.strptime(ymd, '%Y%m%d')

def avg(ticker, avg_back_days,invest, stop_buy, up_cap, up_scale, down_scale):
    print('ticker={}, back days={} invest={} stop buying = {} up cap ={} up scale={} down scale={}'.format(ticker, avg_back_days,invest, stop_buy, up_cap, up_scale, down_scale))
    m = FluxtrateBuy(up_scale, down_scale, stop_buy, up_cap)
    today = datetime.now()
    avg = calc_avg(ticker, today - timedelta(days=1), avg_back_days)
    action = m.calc(today, avg)
    print(action)


if __name__ == "__main__":
    from docopt import docopt

    args = docopt(__doc__)
    #print(args)

    if args['test']:
        back_test(int(args['-d']),
                  int(args['--buy-interval']),
                  int(args['--invest']),
                  parse_datetime(args['-f']),
                  parse_datetime(args['-t']),
                  int(args['--stop-buy']),
                  int(args['--up-scale-limit']),
                  args['<ticker>'])
    elif args['avg']:
        avg(args['<ticker>'][0],
            int(args['-d']),
            int(args['--invest']),
            int(args['--stop-buy']),
            int(args['--up-scale-limit']),
            int(args['--up']),
            int(args['--down'])
        )
