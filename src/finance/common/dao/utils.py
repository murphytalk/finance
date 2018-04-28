# -*- coding: utf-8 -*-
import random
from time import time

TODAY = int(time())
SECONDS_PER_DAY = 60 * 60 * 24
# 2 years ago (epoch seconds)
DAY1 = TODAY - SECONDS_PER_DAY * 356 * 2
STOCK_NUM = 20
FUNDS_NUM = 10
URL = 'http://finance.yahoo.com/'


def gen_symbol(length):
    """
    generate a len letter symbol
    """

    def c():
        return chr(random.randint(ord('A'), ord('Z')))

    s = ''
    for i in range(length):
        s += c()
    return s


def gen_date():
    """
    generate a date between 2014-1-1 to today
    """
    return random.randint(DAY1, TODAY)


def gen_dates():
    """
    :return: a sequence of the epoch representation of each day from DAY1 to today
    """
    return range(DAY1, TODAY + SECONDS_PER_DAY, SECONDS_PER_DAY)


def gen_expense_ratio():
    return random.uniform(0.1, 3)


def gen_price(min_price, max_price):
    return random.uniform(min_price, max_price)


def gen_allocation(parties):
    allocations = {}
    remain = 100
    id = 1
    while True:
        if len(allocations) == parties - 1:
            # the last one
            allocations[id] = remain
            break
        else:
            allocations[id] = random.uniform(1, remain - 1)
            remain -= allocations[id]
        id += 1
    return allocations

