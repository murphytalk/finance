import { NGXLogger } from 'ngx-logger';
import { DataService, Positions, ValuePair, RawPortfolio, PortfolioAllocation, FinPosition, CashBalance } from './../../shared/data.service';
import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';
import { fromEntries, currencyFormatter } from './../../shared/calc';
import { MatRadioChange } from '@angular/material/radio';

interface OverviewItem{
  asset?: string;
  ccy?: string;
  marketValue: number;
  marketValueBaseCcy: number;
  profit: number;
  profitBaseCcy: number;
}

interface PositionAppliedWithPortfolio{
  shares: number;
  capital?: number;
}

interface PortAllocItem{
  alloc: PortfolioAllocation;
  orgAlloc: PortfolioAllocation;
}

interface PortAlloc{
  // key is instrument name
  [key: string]: PortAllocItem;
}

interface Portfolio{
  // key is portfolio name
  [key: string]: PortAlloc;
}

const ALL_PORTFOLIOS = 'All';

@Component({
  selector: 'app-fin-overview',
  templateUrl: './fin-overview.component.html',
  styleUrls: ['./fin-overview.component.scss']
})
export class FinOverviewComponent implements OnInit {
  private positions: Positions;
  private portfolios: Portfolio;

  get portfolioNames(){
    return this.portfolios ? Object.keys(this.portfolios) : [];
  }
  selectedPortfolio = ALL_PORTFOLIOS;
  overviewData: OverviewItem[];

  columnDefs = [
    { headerName: 'Asset', field: 'asset', flex: 1 },
    { headerName: 'Currency', field: 'ccy', flex: 1 },
    { headerName: 'Market Value', field: 'marketValue', valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 },
    { headerName: 'Market Value(JPY)', field: 'marketValueBaseCcy',valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 },
    { headerName: 'Profit', field: 'profit',valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 },
    { headerName: 'Profit(JPY)', field: 'profitBaseCcy',valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 },
  ];

  constructor(
    private data: DataService,
    private logger: NGXLogger
  ) {}

  ngOnInit(): void {
    this.data.getPositions().pipe(first()).subscribe(
      positions => {
        this.logger.debug('positions', positions);
        this.positions = positions;
        this.data.getPortfolios().pipe(first()).subscribe(
          rawPortfolios => {
            this.portfolios = {}; this.portfolios[ALL_PORTFOLIOS] = null ;
            rawPortfolios.forEach( rawPortfolio =>
              this.portfolios[rawPortfolio.name] =  fromEntries( rawPortfolio.allocations.map ( allocation =>
                // a key and value pair
                [ allocation.instrument,
                  { alloc: allocation,
                    // tslint:disable-next-line: max-line-length
                    orgAlloc: {shares: allocation.shares, market_value: allocation.market_value, current_allocation: allocation.current_allocation}
                }])
            ));
            this.logger.debug('converted portfolios', this.portfolios);
            this.refresh();
          }
        );
      },
      err => this.logger.error('Failed to get positions', err),
      () => this.logger.debug('position get done')
    );
  }

  private applyPortfolio(portfolio: PortAlloc, position: FinPosition): PositionAppliedWithPortfolio{
    const instrument = position.instrument.name;

    if (portfolio != null && !(instrument in portfolio)){
      return { shares: -1 };
    }
    return {shares: position.shares, capital: position.capital};
  }

  private calcOverview(assetType: string,
                       calc: (assetType: string, sum: {[key: string]: OverviewItem}) => void): OverviewItem[] {
      // see /finance_demo/api/report/positions
      const sum: {[key: string]: OverviewItem} = {};
      calc(assetType, sum);
      return Object.keys(sum).map( ccy => ({
        asset: assetType,
        ccy,
        marketValue: sum[ccy].marketValue,
        marketValueBaseCcy: sum[ccy].marketValueBaseCcy,
        profit: sum[ccy].profit,
        profitBaseCcy: sum[ccy].profitBaseCcy}));
  }

  private refresh(){
    const portfolio = this.portfolios[this.selectedPortfolio];
    let overview: OverviewItem[] = [];
    const assetTypes = ['ETF', 'Stock', 'Funds'];
    assetTypes.forEach( asset => {
      overview = overview.concat(this.calcOverview(asset, (assetType, sum) => {
        this.positions[assetType].forEach( (position: FinPosition) => {
          const newPos = this.applyPortfolio(portfolio, position);
          const shares  = newPos.shares;
          const capital = newPos.capital;
          if (shares > 0) {
              const marketValue = shares * position.price;
              const marketValueBaseCcy = marketValue * position.xccy;
              const profit = marketValue - capital;
              const profitBaseCcy = profit * position.xccy;
              const ccy = position.ccy;
              if ( ccy in sum){
                sum[ccy].marketValue += marketValue;
                sum[ccy].marketValueBaseCcy += marketValueBaseCcy;
                sum[ccy].profit += profit;
                sum[ccy].profitBaseCcy += profitBaseCcy;
              }
              else{
                sum[ccy] = {marketValue, marketValueBaseCcy, profit, profitBaseCcy};
              }
          }
        });
      }));
    });

    // cash positions
    overview = overview.concat(this.calcOverview('Cash', (assetType, sum) => {
      const cashBalances = this.positions.Cash;
      cashBalances.forEach( balance => {
         if (balance.ccy in sum){
          sum[balance.ccy].marketValue += balance.balance;
          sum[balance.ccy].marketValueBaseCcy += balance.balance * balance.xccy;
        }
        else{
          // tslint:disable-next-line: max-line-length
          sum[balance.ccy] = {marketValue: balance.balance, marketValueBaseCcy: balance.balance * balance.xccy, profit: null, profitBaseCcy: null};
        }
      });
    }));

    this.overviewData = overview;
    this.logger.debug('overview', this.overviewData);
  }

  onPortfolioChanged(e: MatRadioChange){
    this.logger.debug('portfolio changed ', e);
    this.logger.debug('portfolio selected', this.selectedPortfolio);
    this.refresh();
  }
}
