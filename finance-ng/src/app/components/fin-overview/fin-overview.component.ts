import { NGXLogger } from 'ngx-logger';
import { DataService, Positions, PortfolioAllocation, FinPosition } from './../../shared/data.service';
import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';
import { fromEntries, formatNumber, currencySign, pieChartOption, ChartData } from './../../shared/calc';
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

interface PieChartData{
  name?: string;
  y?: number;
}

interface PieChartDataCollect{
  [key: string]: number;
}

const ALL_PORTFOLIOS = 'All';

// for ag-grid
function currencyFormatter(params) {
  // console.log('overview num field param %o', params);
  const overview = params.data as OverviewItem;
  // tslint:disable-next-line: max-line-length
  return params.value == null ? '' :  `${params.colDef.headerName === 'JPY' ? '\u00a5' : currencySign(overview.ccy)} ${formatNumber(params.value)}`;
}


@Component({
  selector: 'app-fin-overview',
  templateUrl: './fin-overview.component.html',
  styleUrls: ['./fin-overview.component.scss']
})
export class FinOverviewComponent implements OnInit {
  private positions: Positions;
  private portfolios: Portfolio;
  private countryAlloc: PieChartDataCollect = {};
  private regionAlloc: PieChartDataCollect = {};
  private assetAlloc: PieChartDataCollect = {};

  get assetAllocPieOption(){
    return this.pieChartOpt(this.assetAlloc);
  }
  get countryAllocPieOption(){
    return this.pieChartOpt(this.countryAlloc);
  }
  get regionAllocPieOption(){
    return this.pieChartOpt(this.regionAlloc);
  }


  get portfolioNames(){
    return this.portfolios ? Object.keys(this.portfolios) : [];
  }
  selectedPortfolio = ALL_PORTFOLIOS;
  overviewData: OverviewItem[];

  columnDefs = [
    { headerName: 'Asset', field: 'asset', flex: 1 },
    { headerName: 'Currency', field: 'ccy', flex: 1 },
    { headerName: 'Market Value' ,  children: [
      { headerName: 'CCY', field: 'marketValue', valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 },
      { headerName: 'JPY', field: 'marketValueBaseCcy', valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 }
    ]},
    { headerName: 'Profit' ,  children: [
     { headerName: 'CCY', field: 'profit', valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 },
     { headerName: 'JPY', field: 'profitBaseCcy', valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 }
    ]}
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
            // transform the shape of position objects
            this.portfolios = {}; this.portfolios[ALL_PORTFOLIOS] = null ;
            rawPortfolios.forEach( rawPortfolio =>
              this.portfolios[rawPortfolio.name] =  fromEntries( rawPortfolio.allocations.map ( allocation =>
                // a key(instrument) and value(position of that instrument) pair
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

  private pieChartOpt(data: PieChartDataCollect){
    return pieChartOption(null, null,
      Object.keys(data).map( key => ({name: key, value: data[key]})));
  }

  private applyPortfolio(portfolio: PortAlloc, position: FinPosition): PositionAppliedWithPortfolio{
    const instrument = position.instrument.name;

    if (portfolio != null && !(instrument in portfolio)){
      return { shares: -1 };
    }
    return {shares: position.shares, capital: position.capital};
  }

  private calcOverview(assetType: string,
                       sumByCcy: (assetType: string, sum: {[key: string]: OverviewItem}) => void): OverviewItem[] {
      // see /finance_demo/api/report/positions
      const sum: {[key: string]: OverviewItem} = {};
      sumByCcy(assetType, sum);
      return Object.keys(sum).map( ccy => ({
        asset: assetType,
        ccy,
        marketValue: sum[ccy].marketValue,
        marketValueBaseCcy: sum[ccy].marketValueBaseCcy,
        profit: sum[ccy].profit,
        profitBaseCcy: sum[ccy].profitBaseCcy}));
  }

  private refresh(){
    function filter_by_allocation(chartData: PieChartDataCollect, shares: number, position: FinPosition, allocationName: string){
      const allocationCollection = allocationName + '_allocation';
      position[allocationCollection].forEach( allocation => {
        const ratio = allocation.ratio / 100.0;
        const value = shares * position.price * ratio * position.xccy;
        const alloc = allocation[allocationName];
        if ( alloc in chartData ){
          chartData[alloc] += value;
        }
        else{
          chartData[alloc] = value;
        }
      });
    }

    this.countryAlloc = {};
    this.regionAlloc = {};
    this.assetAlloc = {};

    const portfolio = this.portfolios[this.selectedPortfolio];
    let overview: OverviewItem[] = [];
    const assetTypes = ['ETF', 'Stock', 'Funds'];
    const allocTypes = ['country', 'region', 'asset'];
    assetTypes.forEach( asset => {
      overview = overview.concat(this.calcOverview(asset, (assetType, sum) => {
        this.positions[assetType].forEach( (position: FinPosition) => {
          const newPos = this.applyPortfolio(portfolio, position);
          const shares  = newPos.shares;
          const capital = newPos.capital;
          if (shares > 0) {

              filter_by_allocation(this.countryAlloc, shares, position, 'country');
              filter_by_allocation(this.regionAlloc, shares, position, 'region');
              filter_by_allocation(this.assetAlloc, shares, position, 'asset');

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

    this.logger.debug('country alloc', this.countryAlloc);
    this.logger.debug('region alloc', this.regionAlloc);
    // cash positions
    if (this.selectedPortfolio === ALL_PORTFOLIOS){
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
    }

    this.overviewData = overview;
    this.logger.debug('overview', this.overviewData);
  }

  onPortfolioChanged(e: MatRadioChange){
    this.logger.debug('portfolio changed ', e);
    this.logger.debug('portfolio selected', this.selectedPortfolio);
    this.refresh();
  }
}
