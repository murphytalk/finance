# -*- coding: utf-8 -*-
class Position:
    def __init__(self,instrument,name):
        self.instrument = instrument
        self.name = name
        self.shares = 0
        self.liquidated = 0 # negative value => money(original value) still in market
        self.fee = 0

    def transaction(self,trans_type,price,shares,fee):
            if trans_type == 'SPLIT':
                # 1 to N share split, here price is the N
                self.shares = self.shares * price 
            else:
                s = shares if trans_type == 'BUY' else -1*shares
                self.shares = self.shares + s
                self.liquidated = self.liquidated - price*s
                self.fee = self.fee + fee

    def __str__(self):
        return "Name=%4s,Shares=%4d,Fee=%6.2f,Liquidated=%10.2f"%(self.name,self.shares,self.fee,self.liquidated)

