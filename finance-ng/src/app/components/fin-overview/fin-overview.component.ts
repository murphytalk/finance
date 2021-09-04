import { NGXLogger } from 'ngx-logger';
import { DataService, Positions, PortfolioAllocation, FinPosition } from './../../shared/data.service';
import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';
import { fromEntries, formatNumber, currencySign, pieChartOption, ChartData } from '../../shared/utils';
import { MatRadioChange } from '@angular/material/radio';

interface OverviewItem {
  asset?: string;
  ccy?: string;
  marketValue?: number;
  marketValueBaseCcy: number;
  profit?: number;
  profitBaseCcy: number;
}

interface PositionAppliedWithPortfolio {
  shares: number;
  capital?: number;
}

interface PortAllocItem {
  alloc: PortfolioAllocation;
  orgAlloc: PortfolioAllocation;
}

interface PortAlloc {
  // key is instrument name
  [key: string]: PortAllocItem;
}

interface Portfolio {
  // key is portfolio name
  [key: string]: PortAlloc;
}

interface DataCollect {
  [key: string]: number;
}

enum DataCategory {
  AssetAlloc,
  CountryAlloc,
  RegionAlloc,
  Stock,
  ETF,
  Funds
}

const ALL_PORTFOLIOS = 'All';

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
  private positions: Positions;
  private portfolios: Portfolio;

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
    return this.portfolios ? Object.keys(this.portfolios) : [];
  }
  selectedPortfolio = ALL_PORTFOLIOS;
  overviewData: OverviewItem[];

  columnDefs = [
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
    private logger: NGXLogger
  ) { }

  ngOnInit(): void {
    this.data.getPositions().pipe(first()).subscribe(
      positions => {
        this.logger.debug('positions', positions);
        this.positions = positions;
        this.data.getPortfolios().pipe(first()).subscribe(
          rawPortfolios => {
            // transform the shape of position objects
            this.portfolios = {}; this.portfolios[ALL_PORTFOLIOS] = null;
            rawPortfolios.forEach(rawPortfolio =>
              this.portfolios[rawPortfolio.name] = fromEntries(rawPortfolio.allocations.map(allocation =>
                // a key(instrument) and value(position of that instrument) pair
                [allocation.instrument,
                {
                  alloc: allocation,
                  // tslint:disable-next-line: max-line-length
                  orgAlloc: { shares: allocation.shares, market_value: allocation.market_value, current_allocation: allocation.current_allocation }
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

  private applyPortfolio(portfolio: PortAlloc, position: FinPosition): PositionAppliedWithPortfolio {
    const instrument = position.instrument.name;

    if (portfolio != null && !(instrument in portfolio)) {
      return { shares: -1 };
    }
    return { shares: position.shares, capital: position.capital };
  }

  private calcOverview(assetType: string,
    sumByCcy: (assetType: string, sum: { [key: string]: OverviewItem }) => void): OverviewItem[] {
    // see /finance_demo/api/report/positions
    const sum: { [key: string]: OverviewItem } = {};
    sumByCcy(assetType, sum);
    return Object.keys(sum).map(ccy => ({
      asset: assetType,
      ccy,
      marketValue: sum[ccy].marketValue,
      marketValueBaseCcy: sum[ccy].marketValueBaseCcy,
      profit: sum[ccy].profit,
      profitBaseCcy: sum[ccy].profitBaseCcy
    }));
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

    const portfolio = this.portfolios[this.selectedPortfolio];
    let overview: OverviewItem[] = [];
    const assetTypes = [DataCategory.ETF, DataCategory.Stock, DataCategory.Funds];
    assetTypes.forEach(asset => {
      const assetName = DataCategory[asset];
      overview = overview.concat(this.calcOverview(assetName, (assetType, sum) => {
        this.positions[assetType].forEach((position: FinPosition) => {
          const newPos = this.applyPortfolio(portfolio, position);
          const shares = newPos.shares;
          const capital = newPos.capital;
          if (shares > 0) {

            filter_by_allocation(this.categorizedData.CountryAlloc, shares, position, 'country');
            filter_by_allocation(this.categorizedData.RegionAlloc, shares, position, 'region');
            filter_by_allocation(this.categorizedData.AssetAlloc, shares, position, 'asset');

            const marketValue = shares * position.price;
            const marketValueBaseCcy = marketValue * position.xccy;
            const profit = marketValue - capital;
            const profitBaseCcy = profit * position.xccy;
            const ccy = position.ccy;


            const pieData = this.categorizedData[assetName];
            const name = position.instrument.name;
            if (name in pieData) {
              pieData[name] += marketValueBaseCcy;
            }
            else {
              pieData[name] = marketValueBaseCcy;
            }

            if (ccy in sum) {
              sum[ccy].marketValue += marketValue;
              sum[ccy].marketValueBaseCcy += marketValueBaseCcy;
              sum[ccy].profit += profit;
              sum[ccy].profitBaseCcy += profitBaseCcy;
            }
            else {
              sum[ccy] = { marketValue, marketValueBaseCcy, profit, profitBaseCcy };
            }
          }
        });
      }));
    });

    // cash positions
    if (this.selectedPortfolio === ALL_PORTFOLIOS) {
      overview = overview.concat(this.calcOverview('Cash', (_, sum) => {
        const cashBalances = this.positions.Cash;
        cashBalances.forEach(balance => {
          if (balance.ccy in sum) {
            sum[balance.ccy].marketValue += balance.balance;
            sum[balance.ccy].marketValueBaseCcy += balance.balance * balance.xccy;
          }
          else {
            // tslint:disable-next-line: max-line-length
            sum[balance.ccy] = { marketValue: balance.balance, marketValueBaseCcy: balance.balance * balance.xccy, profit: null, profitBaseCcy: null };
          }
        });
      }));
    }

    // summery
    const summery = overview.reduce((accu, x) => {
      accu.marketValueBaseCcy += x.marketValueBaseCcy;
      accu.profitBaseCcy += x.profitBaseCcy;
      return accu;
    }, { marketValueBaseCcy: 0, profitBaseCcy: 0 });

    this.overviewData = overview.concat(summery);
    this.logger.debug('overview', this.overviewData);
    this.logger.debug('asset alloc', this.categorizedData.AssetAlloc);
  }

  onPortfolioChanged(e: MatRadioChange) {
    this.logger.debug('portfolio changed ', e);
    this.logger.debug('portfolio selected', this.selectedPortfolio);
    this.refresh();
  }
}
