# -*- coding: utf-8 -*-
"""
Adapters used by the scraper

Login credentials are read from MyInvestMan.ini, its format is:

[BrokerName]
user=my-user-type
pass=my-pass-word

== Other configuration ==

If proxy is needed :
[Proxy]
http=
https=
"""
import sys
import ConfigParser
import sqlite3
from time import time
from config import INI

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.read(INI)

#see if proxy is specified in .ini
#def get_proxy():
#    proxy = None
#    try:
#        http_proxy = config.get('Proxy', 'http')
#        https_proxy = config.get('Proxy', 'https')
#        if http_proxy is not None and https_proxy is not None:
#            proxy = urllib2.ProxyHandler({'http': http_proxy, 'https': https_proxy})
#    except ConfigParser.NoSectionError:
#        pass
#
#    return proxy


class ConsoleAdapter:
    def __init__(self, broker_name):
        self.broker = broker_name
        print "Broker:%s" % broker_name

    def get_login(self):
        return config.get(self.broker, 'user'), config.get(self.broker, 'pass')

    def onData(self, instrument_name, capital, amount, market_value, profit, price):
        print u"{}:amount={},price={},market value={},capital={},profit={}".format(instrument_name,
                                                                                   amount,
                                                                                   price,
                                                                                   market_value,
                                                                                   capital,
                                                                                   profit)
    def close(self):
        pass

class SqliteAdapter(ConsoleAdapter):
    """
    This is an adapter implementation to write to sqlite DB.
    """
    def __init__(self, db_path,broker_name):
        print "Broker:%s" % broker_name        
        self.broker = broker_name
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()

        self.broker_id = self.get_id('broker',broker_name)


    def get_id(self,table,param):
        #insert if we see it first time
        while True:
            self.c.execute('SELECT rowid,name FROM %s WHERE name=?'%table,(param,))
            r = self.c.fetchone()
            if r is None:
                self.c.execute("INSERT INTO %s VALUES (?,NULL,?)"%table,(param,self.broker_id))
                self.conn.commit
            else:
                return r[0]                
                
         
    def onData(self, instrument_name, capital, amount, market_value, profit, price):
        instrument_id = self.get_id('instrument',instrument_name)
        self.c.execute("INSERT INTO performance VALUES (?,?,?,?,?,?,?)",(instrument_id,amount,price,market_value,profit,capital,int(time())))

        

    def close(self):
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":    
    if len(sys.argv) <> 2:
        print("USGAE: adatper <sqlite db file>")
    else:
        from config import BROKERS
        
        conn = sqlite3.connect(sys.argv[1])
        c = conn.cursor()

        for t in(
            'broker (type text)',
            'asset  (type text)',
            'region (type text)'
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

        c.execute("CREATE TABLE instrument (type text not null, asset int null, broker null,currency text not null,  FOREIGN KEY(asset) REFERENCES asset(rowid),FOREIGN KEY(broker) REFERENCES broker(rowid))")
        c.execute("CREATE TABLE [transaction](instrument int not null ,type text not null, price real not null, number int not null, fee real null, date int not null,FOREIGN KEY(instrument) REFERENCES asset(rowid))")
        c.execute("CREATE TABLE performance(instrument int not null ,amount int not null,price real not null, value real not null, profit value not null, capital,date int not null, FOREIGN KEY(instrument) REFERENCES asset(rowid))")
                

        conn.commit()
        conn.close()
