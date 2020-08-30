import { NGXLogger } from 'ngx-logger';
import { DataService, Positions, ValuePair, RawPortfolio, PortfolioAllocation, FinPosition } from './../../shared/data.service';
import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';
import { fromEntries } from './../../shared/calc';

interface OverviewItem{
  asset: string;
  ccy: string;
  marketValue: number;
  marketValueJPY: number;
  profit: number;
  profitJPY: number;
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
const INSTRUMENT_TYPES = ['ETF', 'Stock', 'Funds'];

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
    {headerName: 'Asset', field: 'asset', flex: 1 },
    {headerName: 'Currency', field: 'ccy', flex: 1 },
    {headerName: 'Market Value', field: 'marketValue', flex: 1 },
    {headerName: 'Market Value(JPY)', field: 'marketValueJPY', flex: 1 },
    {headerName: 'Profit', field: 'profit', flex: 1 },
    {headerName: 'Profit(JPY)', field: 'profitJPY', flex: 1 },
  ];

  constructor(
    private data: DataService,
    private logger: NGXLogger
  ) {}

  ngOnInit(): void {
    this.data.getPositions().pipe(first()).subscribe(
      data => {
        this.logger.debug('positions', data);
        this.positions = data;
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

    if (position != null && !(instrument in portfolio)){
      return { shares: -1 };
    }
    return {shares: position.shares, capital: position.capital};
  }

  private refresh(){
    this.logger.debug('converted portfolios', this.portfolios);
  }

  selectPortfolio(portfolio: string){
    this.logger.debug('portfolio selected', portfolio);
  }
}
