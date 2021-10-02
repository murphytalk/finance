import random
import sys
import time
import os.path
from datetime import date
from os import environ

try:
    from finance.common.const import STOCK_START_DATE
except ImportError:
    from const import STOCK_START_DATE

SECONDS_PER_DAY = 3600 * 24


def get_random_dict_value(dict_data, predicate=None):
    while True:
        i = dict_data[random.sample(dict_data.keys(), 1)[0]]
        if predicate is not None:
            if predicate(i):
                return i
        else:
            return i


def get_random_dict_key(dict_data, predicate=None):
    while True:
        i = random.sample(dict_data.keys(), 1)[0]
        if predicate is not None:
            if predicate(i):
                return i
        else:
            return i


def add_lib_to_path(zip):
    if len([x for x in sys.path if x == zip]) == 0:
        sys.path.insert(0, zip)


def get_current_date_epoch():
    return int((time.time() + time.timezone) / SECONDS_PER_DAY) * SECONDS_PER_DAY


def epoch2date(epoch):
    """
    epoch is in UTC, convert it to local date by applying timezone offset
    """
    t = epoch + time.timezone
    return date.fromtimestamp(0 if t < 0 else t)


def str2time(date_str):
    """
    convert a date string to local time
    :param date_str: YYYYMMDD, YYYY/MM/DD, YYYY-MM-DD
    :return: time
    """
    try:
        return time.strptime(date_str, '%Y%m%d')
    except ValueError:
        try:
            return time.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                return time.strptime(date_str, '%Y/%m/%d')
            except ValueError:
                return None


def date2epoch(dt):
    return dt.timestamp() - time.timezone


def date_str2epoch(str_date):
    """
    Convert a string date (local time) to UTC epoch
    :param str_date: YYYYMMDD, YYYY/MM/DD, YYYY-MM-DD in local time
    :return: Unix epoch int UTC
    """
    return time.mktime(str2time(str_date)) - time.timezone


def get_valid_db_from_env(varname, default=None):
    """
    Check if environment variable varname is set and is an existing file
    :param varname: environment variable name
    :param default: default db name
    :return: if varname is set and is an existing file return that name, otherwise return default
    """
    db = environ.get(varname)
    return default if db is None or (not os.path.exists(db)) else db
