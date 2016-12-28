# -*- coding: utf-8 -*-
# !/usr/bin/python2
import sqlite3
import sys

asset = {'stock': 1, 'bond': 2, 'corp': 3, 'reit': 4, 'comm': 5, 'cash': 6, 'other': 7}


def update_asset_allocation(c, instrument_id, asset, ratio):
    c.execute("INSERT INTO asset_allocation values (%s,%s,%s)" % (instrument_id, asset, ratio))


if __name__ == "__main__":
    """
    parameter : 
        -fxxxxxx  path to sqlite db file xxxxx
        -ixxxxxx  instrument id
    	asset,ratio pairs 
    """

    ratios = [x for x in sys.argv[1:] if x[:2] != '-f' and x[:2] != '-i']
    db = [x for x in sys.argv[1:] if x[:2] == '-f']
    instrument = [x for x in sys.argv[1:] if x[:2] == '-i']

    if len(ratios) == 0 or len(db) == 0:
        print ("Bad paramter")
    else:
        db = db[0][2:]
        instrument = instrument[0][2:]

        conn = sqlite3.connect(db)
        c = conn.cursor()

        for rr in ratios:
            a, r = rr.split(',')
            if (a in asset) and (r is not None):
                update_asset_allocation(c, instrument, asset[a], r)

        conn.commit()
        conn.close()
