﻿import sys
import time
from config import set_debug
from const import STOCK_START_DATE
from datetime import datetime,date

SECONDS_PER_DAY = 3600*24

def add_lib_to_path(zip):
    if len([x for x in sys.path if x == zip]) == 0:
        sys.path.insert(0, zip)

def get_utc_offset():
    return -time.timezone

def get_current_date_epoch():
    return int((time.time()+get_utc_offset())/SECONDS_PER_DAY) * SECONDS_PER_DAY

def epoch2datetime(epoch):
    return datetime.fromtimestamp(epoch)

class ScrapError(Exception):
    def __init__(self,  msg):
        self.msg = msg

def cmdline_args(argv,db_adapter_clz = None):
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
        if len(ss)==1:
            try:
                return datetime.strptime(ss[0][2:],'%Y%m%d')
            except ValueError:
                return None
        else:
            return None

    debug_mode_option = '-d'
    set_debug(debug_mode_option in argv)
    args      = [x for x in argv if x != debug_mode_option]

        
    others    = [x for x in args if x[:2] != '-f' and x[:2] != '-s' and x[:2] != '-e']
    db        = [x for x in args if x[:2] == '-f']
    start_date= [x for x in args if x[:2] == '-s']
    end_date  = [x for x in args if x[:2] == '-e']

    start_date = convert_date(start_date)
    end_date   = convert_date(end_date)


    result = None
    if start_date is None:
        start_date = STOCK_START_DATE
    
    if end_date is None:
        end_date = date.today()

    
    result = {}
    result['start_date'] = start_date
    result['end_date']   = end_date
    if len(db)>0:
        result['dbfile'] = db[0][2:]
    else:
        result['dbfile'] = None
        
    return (result,others)
