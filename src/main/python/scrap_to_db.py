# -*- coding: utf-8 -*-
"""
Scrap portfolio performance page from brokers' website.
"""
import sys
from adapter import SqliteAdapter
from scraper import *
from config import BROKERS

if __name__ == '__main__':
    """
    parameter : one or more broker name, or all brokers if no parameter given
    """
    def do_work(broker):
        adapter = SqliteAdapter('finance.db',broker.get_name())
        broker.open(adapter)
        adapter.close()
        
    args = [x for x in sys.argv[1:]]
    proxy = None

    if len(args) == 0:
        for broker in [getattr(sys.modules[__name__], x)(proxy) for x in BROKERS]:
            do_work(broker)
    else:
        for broker_name in args:
            broker_class = getattr(sys.modules[__name__], broker_name)
            do_work(broker_class(proxy))
