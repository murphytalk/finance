import { Injectable } from '@angular/core';
import { NGXLogger } from 'ngx-logger';
import { first } from 'rxjs/operators';
import { fromEntries } from '../shared/utils';
import { CashBalance, DataService, FinPosition, FinPositionByBroker, PortfolioAllocation, Positions } from './data.service';

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

export enum DataCategory {
  AssetAlloc,
  CountryAlloc,
  RegionAlloc,
  Stock,
  ETF,
  Funds
}

export interface AllPosAndPort{
  positions: Positions;
  portfolios: Portfolio;
}

export interface OverviewItem {
  broker?: string;
  asset?: string;
  ccy?: string;
  marketValue?: number;
  marketValueBaseCcy: number;
  profit?: number;
  profitBaseCcy: number;
}

export interface DataCollect {
  [key: string]: number;
}

export const ALL_PORTFOLIOS = 'All';

type SumByCcy = { [key: string]: OverviewItem };
type SumByBrokerCcy = { [key: string]: SumByCcy };

function isCashBalance(o: SumByBrokerCcy | CashBalance): o is CashBalance {
  return (o as CashBalance).xccy !== undefined;
}

@Injectable({
  providedIn: 'root',
})
export class CalcService {
  constructor(private data: DataService, private logger: NGXLogger) {}

  loadPosition(): Promise<AllPosAndPort>{
    return new Promise( (resolve, reject) =>
      this.data.getPositions().pipe(first()).subscribe(
        positions => {
          this.logger.debug('positions', positions);
          this.data.getPortfolios().pipe(first()).subscribe(
            rawPortfolios => {
              // transform the shape of position objects
              const portfolios = {};
              portfolios[ALL_PORTFOLIOS] = null;
              rawPortfolios.forEach(rawPortfolio =>
                portfolios[rawPortfolio.name] = fromEntries(rawPortfolio.allocations.map(allocation =>
                  // a key(instrument) and value(position of that instrument) pair
                  [allocation.instrument,
                  {
                    alloc: allocation,
                    orgAlloc: { shares: allocation.shares, market_value: allocation.market_value, current_allocation: allocation.current_allocation }
                  }])
                ));
              this.logger.debug('converted portfolios', portfolios);
              resolve({positions, portfolios});
            }
          );
        },
        err => reject(err),
        () => this.logger.debug('position get done')
    ));
  }

  private calcOverview(assetType: string,
    sumByBrokerCcy: (assetType: string, sum: SumByBrokerCcy | CashBalance) => void): OverviewItem[] {
    // see /finance/api/report/positions
    const sum: SumByBrokerCcy | CashBalance  = {};
    sumByBrokerCcy(assetType, sum);

    const overviews: OverviewItem[] = [];

    if(isCashBalance(sum)){
      sum.
    }
    else{
    Object.entries(sum).forEach( ([broker, byCcy]) => {
      // broker summary : broker, market value in base ccy, profit in base ccy
      let marketValueBaseCcy = 0;
      let profitBaseCcy = 0;
      Object.entries(byCcy).forEach( ([ccy, overview]) => {
        marketValueBaseCcy += overview.marketValueBaseCcy;
        profitBaseCcy += overview.profitBaseCcy;
      });
      overviews.push({broker, marketValueBaseCcy, profitBaseCcy});
      // items grouped by ccy for this broker
      overviews.concat(Object.entries(byCcy).map(([ccy, overview]) =>  ({
          asset: assetType,
          ccy,
          marketValue: overview.marketValue,
          marketValueBaseCcy: overview.marketValueBaseCcy,
          profit: overview.profit,
          profitBaseCcy: overview.profitBaseCcy
      })));
    });
    }

    return overviews;
  }

  private applyPortfolio(portfolio: PortAlloc, position: FinPosition): PositionAppliedWithPortfolio {
    const instrument = position.instrument.name;

    if (portfolio != null && !(instrument in portfolio)) {
      return { shares: -1 };
    }
    return { shares: position.shares, capital: position.capital };
  }

  getPositionOverviewByPortfolio(all: AllPosAndPort, portfolioName: string,
                                 onFilteredPosition: (assetName:string, position :FinPosition, shares: number, mktValueBaseCcy: number) => void ): OverviewItem[] {
    const portfolio = all.portfolios[portfolioName];

    let overview: OverviewItem[] = [];
    const assetTypes = [DataCategory.ETF, DataCategory.Stock, DataCategory.Funds];
    assetTypes.forEach(asset => {
      const assetType = DataCategory[asset];
      overview = overview.concat(this.calcOverview(assetType, (theAssetType, sum) => {
        const p: FinPositionByBroker = all.positions[theAssetType];
        Object.entries(p).forEach( ([broker, position]) => {
          const newPos = this.applyPortfolio(portfolio, position);
          const shares = newPos.shares;
          const capital = newPos.capital;
          // apply portfolio
          const marketValue = shares * position.price;
          const marketValueBaseCcy = marketValue * position.xccy;
          const profit = marketValue - capital;
          const profitBaseCcy = profit * position.xccy;
          const ccy = position.ccy;

          if (shares > 0) {
            let byCcy: SumByCcy;
            if (broker in sum){
              byCcy = sum[broker];
            }
            else{
              byCcy = {};
              sum[broker] = byCcy;
            }

            if(ccy in byCcy){
              byCcy[ccy].marketValue += marketValue;
              byCcy[ccy].marketValueBaseCcy += marketValueBaseCcy;
              byCcy[ccy].profit += profit;
              byCcy[ccy].profitBaseCcy += profitBaseCcy;
            }
            else {
              byCcy[ccy] = { marketValue, marketValueBaseCcy, profit, profitBaseCcy };
            }

            onFilteredPosition(theAssetType, position, shares, marketValueBaseCcy);
          }
        });
      }));
    });

    // cash positions
    if (portfolioName === ALL_PORTFOLIOS) {
      overview = overview.concat(this.calcOverview('Cash', (_, sum ) => {
        const cashBalances = all.positions.Cash;
        cashBalances.forEach(balance => {
          if (balance.ccy in sum) {
            sum[balance.ccy].marketValue += balance.balance;
            sum[balance.ccy].marketValueBaseCcy += balance.balance * balance.xccy;
          }
          else {
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

    return overview.concat(summery);
  }
}
