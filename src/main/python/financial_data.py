# -*- coding: utf-8 -*-
"""
Scrap public financial data
"""
import sys
from scraper import Xccy
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
    def do_work(db,provider):
        if db is None:
            adapter = ConsoleAdapter(provider.get_name())
        else:
            adapter = SqliteAdapter2(db,provider.get_name())
        provider.open(adapter)
        adapter.close()


    proxy = None

    args,providers = cmdline_args(sys.argv[1:])

    if args is None:
        sys.exit()

    
    if len(providers) == 0:
        for provider in [getattr(sys.modules[__name__], x)(args['start_date'],args['end_date'],proxy) for x in FINANCIAL_DATA]:
            do_work(args['dbfile'],provider)
    else:
        for provider_name in providers:
            provider_class = getattr(sys.modules[__name__], provider_name)
            do_work(args['dbfile'],provider_class(args['start_date'],args['end_date']))
