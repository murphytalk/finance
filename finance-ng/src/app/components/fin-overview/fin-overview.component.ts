import { NGXLogger } from 'ngx-logger';
import { DataService, Positions, ValuePair, Portfolios, Portfolio } from './../../shared/data.service';
import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

interface OverviewItem{
  asset: string;
  ccy: string;
  marketValue: number;
  marketValueJPY: number;
  profit: number;
  profitJPY: number;
}

interface PositionResult{
  shares: number;
  capital?: number;
}

@Component({
  selector: 'app-fin-overview',
  templateUrl: './fin-overview.component.html',
  styleUrls: ['./fin-overview.component.scss']
})
export class FinOverviewComponent implements OnInit {
  private positions: Positions;
  private portfolios: Portfolio[];

  get portfolioNames(){
    const names = ['All'];
    return this.portfolios ? names.concat(this.portfolios.map( x => x.name)) : name;
  }
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
          portfolios => this.calculate(portfolios)
        );
      },
      err => this.logger.error('Failed to get positions', err),
      () => this.logger.debug('position get done')
    );
  }

  //private applyPortfolio()

  private calculate(portfolios: Portfolios){
    this.portfolios = portfolios;
    this.overviewData = [
    ] ;
  }

  selectPortfolio(portfolio: string){
    this.logger.debug('portfolio selected', portfolio);
  }
}
