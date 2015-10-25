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
    parameter : 
        -fxxxxxx  path to sqlite db file xxxxx
    	one or more broker name, or all brokers if no parameter given 
    """
    def do_work(db,broker):
        adapter = SqliteAdapter(db,broker.get_name())
        broker.open(adapter)
        adapter.close()
        
    brokers = [x for x in sys.argv[1:] if x[:2] != '-f']
    db  = [x for x in sys.argv[1:] if x[:2] == '-f']
   
    if len(db) == 0:
	print "need path to sqlite db"
	sys.exit()
    else:
	db = db[0][2:]

	    

    proxy = None

    if len(brokers) == 0:
        for broker in [getattr(sys.modules[__name__], x)(proxy) for x in BROKERS]:
            do_work(db,broker)
    else:
        for broker_name in brokers:
            broker_class = getattr(sys.modules[__name__], broker_name)
            do_work(db,broker_class(proxy))
