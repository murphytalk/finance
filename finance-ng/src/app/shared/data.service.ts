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

    getPortfolios(){
      return this.httpClient.get<RawPortfolio[]>(this.url('report/portfolios'));
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

export interface FinPosition {
    instrument: Instrument;
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
    ETF: FinPosition[];
    Stoc: FinPosition[];
    Funds: FinPosition[];
    Cash: CashBalance[];
}

export interface ValuePair{
    ccy: number;
    jpy: number;
}

export interface PortfolioAllocation{
    instrument?: string;
    price?: number;
    target_allocation?: number;
    shares: number;
    market_value: number;
    current_allocation: number;
}

export interface RawPortfolio{
    name: string;
    allocations: PortfolioAllocation[];
}
