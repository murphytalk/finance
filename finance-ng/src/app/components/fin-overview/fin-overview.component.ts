import { NGXLogger } from 'ngx-logger';
import { DataService, Positions, PortfolioAllocation, FinPosition } from './../../services/data.service';
import { Component, OnInit } from '@angular/core';
import { fromEntries, formatNumber, currencySign, pieChartOption, ChartData } from '../../shared/utils';
import { MatRadioChange } from '@angular/material/radio';
import { AllPosAndPort, ALL_PORTFOLIOS, CalcService, DataCategory, DataCollect, OverviewItem } from 'src/app/services/calc.service';




// for ag-grid
function currencyFormatter(params) {
  // console.log('overview num field param %o', params);
  const overview = params.data as OverviewItem;
  // tslint:disable-next-line: max-line-length
  return params.value == null ? '' : `${params.colDef.headerName === 'JPY' ? '\u00a5' : currencySign(overview.ccy)} ${formatNumber(params.value)}`;
}

@Component({
  selector: 'app-fin-overview',
  templateUrl: './fin-overview.component.html',
  styleUrls: ['./fin-overview.component.scss']
})
export class FinOverviewComponent implements OnInit {
  private allPos: AllPosAndPort;

  private categorizedData: { -readonly [key in keyof typeof DataCategory]: DataCollect } = {
    AssetAlloc: {},
    CountryAlloc: {},
    RegionAlloc: {},
    Stock: {},
    ETF: {},
    Funds: {},
  };

  get assetAllocPieOption() {
    return this.pieChartOpt(this.categorizedData.AssetAlloc);
  }
  get countryAllocPieOption() {
    return this.pieChartOpt(this.categorizedData.CountryAlloc);
  }
  get regionAllocPieOption() {
    return this.pieChartOpt(this.categorizedData.RegionAlloc);
  }
  get stockPieOption() {
    return this.pieChartOpt(this.categorizedData.Stock);
  }
  get etfPieOption() {
    return this.pieChartOpt(this.categorizedData.ETF);
  }
  get stockAndEtfPieOption() {
    return this.pieChartOpt(this.stockAndEtfData());
  }
  get fundsPieOption() {
    return this.pieChartOpt(this.categorizedData.Funds);
  }

  get assetTotalValue() {
    return this.pieChartTotalValue(this.categorizedData.AssetAlloc);
  }
  get regionTotalValue() {
    return this.pieChartTotalValue(this.categorizedData.RegionAlloc);
  }
  get countryTotalValue() {
    return this.pieChartTotalValue(this.categorizedData.CountryAlloc);
  }
  get stockTotalValue() {
    return this.pieChartTotalValue(this.categorizedData.Stock);
  }
  get etfTotalValue() {
    return this.pieChartTotalValue(this.categorizedData.ETF);
  }
  get stockAndEtfTotalValue() {
    return this.pieChartTotalValue(this.stockAndEtfData());
  }
  get fundsTotalValue() {
    return this.pieChartTotalValue(this.categorizedData.Funds);
  }

  get portfolioNames() {
    return this.allPos.portfolios ? Object.keys(this.allPos.portfolios) : [];
  }

  selectedPortfolio = ALL_PORTFOLIOS;
  overviewData: OverviewItem[];

  columnDefs = [
    { headerName: 'Broker', field: 'broker', flex: 1 },
    { headerName: 'Asset', field: 'asset', flex: 1 },
    { headerName: 'Currency', field: 'ccy', flex: 1 },
    {
      headerName: 'Market Value', children: [
        { headerName: 'CCY', field: 'marketValue', valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 },
        { headerName: 'JPY', field: 'marketValueBaseCcy', valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 }
      ]
    },
    {
      headerName: 'Profit', children: [
        { headerName: 'CCY', field: 'profit', valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 },
        { headerName: 'JPY', field: 'profitBaseCcy', valueFormatter: currencyFormatter, type: 'numericColumn', flex: 2 }
      ]
    }
  ];

  defaultColDef = {
    //sortable: true,
    resizable: true,
    //floatingFilter: true,
  };

  rowClassRules = {
    sumRow: params => params.data.asset == null
  };

  constructor(
    private data: DataService,
    private calc: CalcService,
    private logger: NGXLogger
  ) { }

  ngOnInit(): void {
    this.calc.loadPosition()
      .then ( all => {
          this.allPos = all;
          this.refresh();
      })
      .catch ( err => this.logger.error('Failed to load positions', err));
  }

  private stockAndEtfData(): DataCollect {
    let stockAndEtf = Object.assign({}, this.categorizedData.ETF);
    stockAndEtf = Object.assign(stockAndEtf, this.categorizedData.Stock);
    return stockAndEtf;
  }

  private pieChartOpt(data: DataCollect) {
    return pieChartOption(null, null,
      Object.keys(data).map(key => ({ name: key, value: data[key] })));
  }

  private pieChartTotalValue(data: DataCollect) {
    return Object.keys(data).map(key => data[key]).reduce((accu, cur) => accu + cur, 0);
  }

  private refresh() {
    function filter_by_allocation(chartData: DataCollect, shares: number, position: FinPosition, allocationName: string) {
      const allocationCollection = allocationName + '_allocation';
      const totalValue = shares * position.price * position.xccy;
      position[allocationCollection].forEach(allocation => {
        const ratio = allocation.ratio / 100.0;
        const alloc = allocation[allocationName];
        const value = totalValue * ratio;
        if (alloc in chartData) {
          chartData[alloc] += value;
        }
        else {
          chartData[alloc] = value;
        }
      });
    }

    this.categorizedData.CountryAlloc = {};
    this.categorizedData.RegionAlloc = {};
    this.categorizedData.AssetAlloc = {};
    this.categorizedData.ETF = {};
    this.categorizedData.Stock = {};
    this.categorizedData.Funds = {};

    this.overviewData = this.calc.getPositionOverviewByPortfolio(this.allPos, this.selectedPortfolio,
      (assetType, position, shares, marketValueBaseCcy) => {
            filter_by_allocation(this.categorizedData.CountryAlloc, shares, position, 'country');
            filter_by_allocation(this.categorizedData.RegionAlloc, shares, position, 'region');
            filter_by_allocation(this.categorizedData.AssetAlloc, shares, position, 'asset');

            const pieData = this.categorizedData[assetType];
            const name = position.instrument.name;
            if (name in pieData) {
              pieData[name] += marketValueBaseCcy;
            }
            else {
              pieData[name] = marketValueBaseCcy;
            }
      });
    this.logger.debug('overview', this.overviewData);
    this.logger.debug('asset alloc', this.categorizedData.AssetAlloc);
  }

  onPortfolioChanged(e: MatRadioChange) {
    this.logger.debug('portfolio changed ', e);
    this.logger.debug('portfolio selected', this.selectedPortfolio);
    this.refresh();
  }
}
