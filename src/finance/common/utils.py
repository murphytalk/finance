import random
import sys
import time
import os.path
from datetime import datetime, date
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
    return date.fromtimestamp(epoch + time.timezone)


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


def cmdline_args(argv, db_adapter_clz=None):
    """
    ConfigParser in stdlib is overkill, this is my poor man's ConfigParser

    parameter :
         argv : sys.argv[1:]

    process the following cmd line arguments:

        -d debug mode
        -fxxxxxx  path to sqlite db file xxxxx
                  if -f not spcified then output to stdout

        -sYYYYMMDD start date
        -eYYYYMMDD end date

    return: ({processed arg name:value},[not processed arguments])
        processed arg names :
          start_date
          end_date
          dbfile
    """

    def convert_date(ss):
        if len(ss) == 1:
            try:
                return datetime.strptime(ss[0][2:], '%Y%m%d')
            except ValueError:
                return None
        else:
            return None

    debug_mode_option = '-d'
    args = [x for x in argv if x != debug_mode_option]

    result = {'debug': debug_mode_option in argv}

    others = [x for x in args if x[:2] != '-f' and x[:2] != '-s' and x[:2] != '-e']
    db = [x for x in args if x[:2] == '-f']
    start_date = [x for x in args if x[:2] == '-s']
    end_date = [x for x in args if x[:2] == '-e']

    start_date = convert_date(start_date)
    end_date = convert_date(end_date)

    if start_date is None:
        start_date = STOCK_START_DATE

    if end_date is None:
        end_date = date.today()

    result['start_date'] = start_date
    result['end_date'] = end_date
    if len(db) > 0:
        result['dbfile'] = db[0][2:]
    else:
        result['dbfile'] = None

    return result, others
