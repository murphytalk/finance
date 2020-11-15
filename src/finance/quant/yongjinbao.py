#!/usr/bin/env python
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
import requests

@dataclass
class Trans:
    dt: datetime
    sym: str
    side: str
    shares: int
    price: float
    cost: float

def parse(xls, skiprows):
    df = pd.read_excel(xls,skiprows=skiprows)
    #trans = df[ df['证券代码'].str.startswith('510') & (df['业务标志'].str.contains('买入') | df['业务标志'].str.contains('卖出'))]
    trans = df[ df['业务标志'].str.contains('买入') | df['业务标志'].str.contains('卖出')]
    filtered=trans.loc[:,['日期','证券代码','业务标志','发生数量','成交均价','佣金','印花税','其他费']]
    return [ Trans(datetime.strptime(str(row['日期']), '%Y%m%d'),
                   row['证券代码'], 'BUY' if row['业务标志'] == '证券买入' else 'SELL',
                   abs(int(row['发生数量'])),
                   float(row['成交均价']),
                   float(row['佣金']) + float(row['印花税']) + float(row['其他费']))  for idx, row in filtered.iterrows()]

def submit_trade(trans):
    r = requests.post('http://localhost:8080/finance/api/transaction/stock/' + "%s.SS"%trans.sym,
                      #auth=(API_USER, API_PASS),
                      json={'Date': datetime.strftime(trans.dt, '%Y%m%d'),
                            'Fee': trans.cost, 'Shares': trans.shares, 'Price': trans.price, 'Type': trans.side})
    print(r)

if __name__ == "__main__":
    trans = parse('62237150对账单/2015.xls',
                  [x for x in range(19)] +  #19 => row num of 流水明细
                  [x for x in range(30,34)])#30 => row num of the last row
    trans +=parse('62237150对账单/2016.xls',
                  [x for x in range(19)] +  #19 => row num of 流水明细
                  [x for x in range(30,34)])#30 => row num of the last row
    trans +=parse('62237150对账单/2017.xls',
                  [x for x in range(20)] +  #19 => row num of 流水明细
                  [x for x in range(112,117)])#30 => row num of the last row
    trans +=parse('62237150对账单/2018.xls',
                  [x for x in range(23)] +  #19 => row num of 流水明细
                  [x for x in range(239,246)])#30 => row num of the last row
    trans +=parse('62237150对账单/2019.xls',
                  [x for x in range(23)] +  #19 => row num of 流水明细
                  [x for x in range(87,91)])#30 => row num of the last row
    trans +=parse('62237150对账单/2020.xls',
                  [x for x in range(22)] +  #19 => row num of 流水明细
                  [x for x in range(101,109)])#30 => row num of the last row
    #trans = [x for x in trans if x.dt.year == 2018]
    #print(trans)
    for t in trans:
        submit_trade(t)
