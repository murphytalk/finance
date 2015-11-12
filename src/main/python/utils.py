import sys
import time

def add_lib_to_path(zip):
    if len([x for x in sys.path if x == zip]) == 0:
        sys.path.insert(0, zip)

def get_utc_offset():
    return -time.timezone


class ScrapError(Exception):
    def __init__(self,  msg):
        self.msg = msg
