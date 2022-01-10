import { TestBed } from '@angular/core/testing';
import { LoggerTestingModule } from 'ngx-logger/testing';

import { AllPosAndPort, ALL_PORTFOLIOS, CalcService } from './calc.service';
import { DataService, FinPosition, FinPositionByBroker, Instrument } from './data.service';


describe('CalcService', () => {
  let service: CalcService;
  let dataServiceSpy: jasmine.SpyObj<DataService>;

  const etf1: Instrument = {id: 10, name: 'ETF 1'};
  const etf2: Instrument = {id: 11, name: 'ETF 2'};
  const stock1: Instrument = {id: 1, name: 'Stock 1'};
  const stock2: Instrument = {id: 2, name: 'Stock 2'};
  const funds1: Instrument = {id: 3, name: 'Funds 1'};
  const funds2: Instrument = {id: 4, name: 'Funds 2'};

  let allPosAndPort: AllPosAndPort = {
    positions: {
      ETF: {
        b1: [
          {
            instrument: etf1,
            asset_allocation: [
              {asset: 'Stock', ratio: 100},
            ],
            country_allocation: [
              {country: 'US', ratio: 100},
            ],
            region_allocation: [
              {region: 'America', ratio: 100},
            ],
            ccy: 'USD',
            xccy: 115,
            shares: 10,
            price: 100,
            capital: 50
          },
          {
            instrument: etf2,
            asset_allocation: [
              {asset: 'Stock', ratio: 100},
            ],
            country_allocation: [
              {country: 'US', ratio: 10},
              {country: 'Japan', ratio: 90},
            ],
            region_allocation: [
              {region: 'America', ratio: 10},
              {region: 'Asia', ratio: 90},
            ],
            ccy: 'USD',
            xccy: 115,
            shares: 100,
            price: 200,
            capital: 30000
          },
        ]
      },
      Stock: {
        b1: [
          {
            instrument: stock1,
            asset_allocation: [
              {asset: 'Stock', ratio: 100},
            ],
            country_allocation: [
              {country: 'US', ratio: 100},
            ],
            region_allocation: [
              {region: 'America', ratio: 100},
            ],
            ccy: 'USD',
            xccy: 115,
            shares: 20,
            price: 100,
            capital: 1000
          },
         ],
         b2: [
          {
            instrument: stock1,
            asset_allocation: [
              {asset: 'Stock', ratio: 100},
            ],
            country_allocation: [
              {country: 'US', ratio: 100},
            ],
            region_allocation: [
              {region: 'America', ratio: 100},
            ],
            ccy: 'USD',
            xccy: 115,
            shares: 20,
            price: 100,
            capital: 1000
          },
           {
            instrument: stock2,
            asset_allocation: [
              {asset: 'Stock', ratio: 100},
            ],
            country_allocation: [
              {country: 'US', ratio: 10},
              {country: 'Japan', ratio: 90},
            ],
            region_allocation: [
              {region: 'America', ratio: 10},
              {region: 'Asia', ratio: 90},
            ],
            ccy: 'USD',
            xccy: 115,
            shares: 100,
            price: 200,
            capital: 30000
          },
         ]
      },
      Funds: {
        b1:[
          {
            instrument: funds1,
            asset_allocation: [
              {asset: 'Stock', ratio: 100},
            ],
            country_allocation: [
              {country: 'US', ratio: 100},
            ],
            region_allocation: [
              {region: 'America', ratio: 100},
            ],
            ccy: 'USD',
            xccy: 115,
            shares: 10,
            price: 100,
            capital: 50
          },
          {
            instrument: funds2,
            asset_allocation: [
              {asset: 'Stock', ratio: 100},
            ],
            country_allocation: [
              {country: 'US', ratio: 100},
            ],
            region_allocation: [
              {region: 'America', ratio: 100},
            ],
            ccy: 'USD',
            xccy: 115,
            shares: 10,
            price: 100,
            capital: 50
          },
        ],
        b3:[
          {
            instrument: funds1,
            asset_allocation: [
              {asset: 'Stock', ratio: 100},
            ],
            country_allocation: [
              {country: 'US', ratio: 100},
            ],
            region_allocation: [
              {region: 'America', ratio: 100},
            ],
            ccy: 'USD',
            xccy: 115,
            shares: 10,
            price: 100,
            capital: 50
          },
          {
            instrument: funds2,
            asset_allocation: [
              {asset: 'Stock', ratio: 100},
            ],
            country_allocation: [
              {country: 'US', ratio: 100},
            ],
            region_allocation: [
              {region: 'America', ratio: 100},
            ],
            ccy: 'USD',
            xccy: 115,
            shares: 10,
            price: 100,
            capital: 50
          },
        ],
      },
      Cash: {
        b1: [
          {ccy: 'USD', balance: 1000, xccy: 115},
          {ccy: 'JPY', balance: 1000, xccy: 1},
          {ccy: 'EUR', balance: 1000, xccy: 200},
        ],
        b2: [
          {ccy: 'USD', balance: 2000, xccy: 115},
          {ccy: 'JPY', balance: 2000, xccy: 1},
          {ccy: 'EUR', balance: 2000, xccy: 200},
        ],
        b3: [
          {ccy: 'JPY', balance: 1000, xccy: 1},
        ],
      }
    },
    portfolios: {
      p1: {
        'ETF 1': {
          alloc: {
            instrument: 'ETF 1',
            shares: 10,
            market_value: 1000,
            current_allocation: 10
          },
          orgAlloc: {
            instrument: 'ETF 1',
            shares: 10,
            market_value: 1000,
            current_allocation: 10
          },
       },
      },
      p2: {
        'ETF 1': {
          alloc: {
            instrument: 'ETF 1',
            shares: 10,
            market_value: 1000,
            current_allocation: 10
          },
          orgAlloc: {
            instrument: 'ETF 1',
            shares: 10,
            market_value: 1000,
            current_allocation: 10
          },
        },
        'Stock 1': {
          alloc: {
            instrument: 'Stock 1',
            shares: 10,
            market_value: 1000,
            current_allocation: 10
          },
          orgAlloc: {
            instrument: 'Stock 1',
            shares: 10,
            market_value: 1000,
            current_allocation: 10
          },
       },
      },
     }
  };

  beforeEach(() => {
    const spy = jasmine.createSpyObj('DataService', ['getPositions']);

    TestBed.configureTestingModule({
      imports: [
        LoggerTestingModule,
      ],
      providers: [
        CalcService, { provide: DataService, useValue: spy }
      ]
    });
    service = TestBed.inject(CalcService);
    dataServiceSpy = TestBed.inject(DataService) as jasmine.SpyObj<DataService>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('When all portfolios specified  getPositionOverviewByPortfolio should return overview of all positions', () => {
    const overviews = service.getPositionOverviewByPortfolio(allPosAndPort, ALL_PORTFOLIOS, () => {})
    console.log(overviews);
  });
});
