import { NGXLogger } from 'ngx-logger';
import { DataService, Positions, ValuePair } from './../../shared/data.service';
import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

interface OverviewItem2{
  asset: string;
  marketValue: ValuePair;
  profit: ValuePair;
}

interface OverviewItem{
  asset: string;
  ccy: string;
  marketValue: number;
  marketValueJPY: number;
  profit: number;
  profitJPY: number;
}


@Component({
  selector: 'app-fin-overview',
  templateUrl: './fin-overview.component.html',
  styleUrls: ['./fin-overview.component.scss']
})
export class FinOverviewComponent implements OnInit {
  private positions: Positions;

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

        this.overviewData = [
          {asset: 'Stock',ccy:'JPY',marketValue:1234,marketValueJPY:1234,profit:12,profitJPY:123}
        ];

      },
      err => this.logger.error('Failed to get positions', err),
      () => this.logger.debug('position get done')
    );
  }

}
