import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
    providedIn: 'root',
})
export class DataService {
    constructor(private httpClient: HttpClient) {}

    private url(path: string){
        return `/finance/api/${path}`;
    }

    getPositions(){
      return this.httpClient.get<Positions>(this.url('report/positions'));
    }
}

export interface Instrument {
    id: number;
    name: string;
}

export interface AssetAllocation {
    asset: string;
    ratio: number;
}

export interface CountryAllocation {
    country: string;
    ratio: number;
}

export interface RegionAllocation {
    region: string;
    ratio: number;
}

export interface Position {
    Instrument: Instrument;
    asset_allocation: AssetAllocation;
    country_allocation: CountryAllocation;
    region_allocation: RegionAllocation;
    ccy: string;
    xccy: number;
    shares: number;
    price: number;
    capital: number;
}

export interface CashBalance {
    ccy: string;
    broker: string;
    balance: number;
    xccy: number;
}

export interface Positions {
    ETF: Position;
    Stoc: Position;
    Funds: Position;
    Cash: CashBalance;
}

export interface ValuePair{
    ccy: number;
    jpy: number;
}
