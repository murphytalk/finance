# -*- coding: utf-8 -*-
"""
Adapters used by the scraper
"""
import sys
import sqlite3

class SqliteAdapter:
    """
    This is an adapter implementation to write to sqlite DB.
    """
    def __init__():
        pass

if __name__ == "__main__":    
    if len(sys.argv) <> 2:
        print("USGAE: adatper <sqlite db file>")
    else:
        from config import BROKERS
        
        conn = sqlite3.connect(sys.argv[1])
        c = conn.cursor()

        for t in(
            'broker (name text)',
            'asset  (type text)',
            'region (name text)'
            ):
               c.execute("CREATE TABLE %s"%t)


        #init broker table
        for b in BROKERS:
            c.execute("INSERT INTO broker values ('%s')"%b)
            
        #init asset table
        for b in ('ETF','Stock','Funds'):
            c.execute("INSERT INTO asset values ('%s')"%b)

        #init region
        for b in ('US','Europe','S.Korea','China','Japan'):
            c.execute("INSERT INTO region values ('%s')"%b)

        c.execute("CREATE TABLE instrument (name text not null, asset int not null, broker null, FOREIGN KEY(asset) REFERENCES asset(rowid),FOREIGN KEY(broker) REFERENCES broker(rowid))")
        c.execute("CREATE TABLE [transaction](instrument int not null ,type text not null, price real not null, number not null, fee real null, date int not null,FOREIGN KEY(instrument) REFERENCES asset(rowid))"
        c.execute("CREATE TABLE performance(instrument int not null ,amount int not null,price real not null, value real not null, profit value not null, capital,date int not null, FOREIGN KEY(instrument) REFERENCES asset(rowid))")
                

        conn.commit()
        conn.close()
