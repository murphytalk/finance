import { NGXLogger } from 'ngx-logger';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { shareReplay } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  private positionCache$: Observable<Positions>;
  private portfolioCache$: Observable<RawPortfolio[]>;

  constructor(
    private logger: NGXLogger,
    private httpClient: HttpClient
  ) { }

  private url(path: string) {
    return `${environment.financeHost}/api/${path}`;
  }

  getPositions() {
    if (!this.positionCache$) {
      this.positionCache$ = this.httpClient.get<Positions>(this.url('report/positions')).pipe(shareReplay(1));
    }
    return this.positionCache$;
  }

  getPortfolios() {
    if (!this.portfolioCache$) {
      this.portfolioCache$ = this.httpClient.get<RawPortfolio[]>(this.url('report/portfolios')).pipe(shareReplay(1));
    }
    return this.portfolioCache$;
  }

  getFundPosition(){
    return this.httpClient.get<FundPosition[]>(this.url('report/fund'));
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
  asset_allocation: AssetAllocation[];
  country_allocation: CountryAllocation[];
  region_allocation: RegionAllocation[];
  ccy: string;
  xccy: number;
  shares: number;
  price: number;
  capital: number;
}

export interface FinPositionByBroker {
  [key: string]: FinPosition[];
}

export interface CashBalance {
  ccy: string;
  balance: number;
  xccy: number;
}

export interface CashBalanceByBroker {
  [key: string]: CashBalance[];
}

export interface Positions {
  ETF: FinPositionByBroker;
  Stock: FinPositionByBroker;
  Funds: FinPositionByBroker;
  Cash: CashBalanceByBroker;
}

export interface ValuePair {
  ccy: number;
  jpy: number;
}

export interface PortfolioAllocation {
  instrument?: string;
  price?: number;
  target_allocation?: number;
  shares: number;
  market_value: number;
  current_allocation: number;
}

export interface RawPortfolio {
  name: string;
  allocations: PortfolioAllocation[];
}

export interface FundPosition {
  broker: string;
  name: string;
  expense_ration: number;
  price: number;
  amount: number;
  capital: number;
  value: number;
  porfit: number;
  date: string | Date;
  instrument_id: number;
  url: string;
}
