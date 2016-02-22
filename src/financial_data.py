# -*- coding: utf-8 -*-
"""
Scrap public financial data
"""
import sys
from scraper import Xccy,Yahoo
from adapter import *
from utils import cmdline_args
from config import FINANCIAL_DATA

if __name__ == '__main__':
    """
    parameter :
        -d debug mode
        -fxxxxxx  path to sqlite db file xxxxx
                  if -f not spcified then output to stdout

        -sYYYYMMDD start date
        -eYYYYMMDD end date
                  
        one or more financial data provider, or all if no parameter given
    """
    def do_work(adapter,providers):
        for provider in providers:     
            provider.open(adapter)
            
    proxy = None
    args,providers = cmdline_args(sys.argv[1:])

    if args is None:
        sys.exit()

    db = args['dbfile']
    n = 'Public finance data'
    if db is None:
        adapter = ConsoleAdapter(n)
    else:
        adapter = SqliteAdapter(db,n,False)
        adapter.load_stock_symbols()

    
    if len(providers) == 0:
        if db is None:
            p = []
        else:
            p = [Yahoo(x,args['start_date'],args['end_date'],proxy) for x in adapter.stocks]
            #p.append(Xccy('Xccy',args['start_date'],args['end_date'],proxy))
    else:
        p = [ Xccy('Xccy',args['start_date'],args['end_date'],proxy) if x == 'Xccy' else Yahoo(x,args['start_date'],args['end_date'],proxy) for x in providers]
        
    do_work(adapter,p)
    adapter.close()
