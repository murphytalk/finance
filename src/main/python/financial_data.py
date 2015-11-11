# -*- coding: utf-8 -*-
"""
Scrap public financial data
"""
import sys
from scraper import set_debug,Xccy
from adapter import *
from config import FINANCIAL_DATA
from datetime import datetime,date

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
        if len(db) == 0:
            adapter = ConsoleAdapter(provider.get_name())
        else:
            db = db[0][2:]
            adapter = SqliteAdapter2(db,provider.get_name())
        provider.open(adapter)
        adapter.close()

    def convert_date(ss):
        if len(ss)==1:
            try:
                return datetime.strptime(ss[0][2:],'%Y%m%d')
            except ValueError:
                return None
        else:
            return date.today()

    proxy     = None
    
    debug_mode_option = '-d'
    set_debug(debug_mode_option in sys.argv[1:])
    args      = [x for x in sys.argv[1:] if x != debug_mode_option]
    
    providers = [x for x in args if x[:2] != '-f' and x[:2] != '-s' and x[:2] != '-e']
    db        = [x for x in args if x[:2] == '-f']
    start_date= [x for x in args if x[:2] == '-s']
    end_date  = [x for x in args if x[:2] == '-e']

    start_date = convert_date(start_date)
    end_date   = convert_date(end_date)

    if start_date is None:
        print "invalid start date"
        sys.exit()
    
    if end_date is None:
        print "invalid end date"
        sys.exit()
    
    
    if len(providers) == 0:
        for provider in [getattr(sys.modules[__name__], x)(start_date,end_date,proxy) for x in FINANCIAL_DATA]:
            do_work(db,provider)
    else:
        for provider_name in providers:
            provider_class = getattr(sys.modules[__name__], provider_name)
            do_work(db,provider_class(start_date,end_date,proxy))
    
